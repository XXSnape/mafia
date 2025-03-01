import asyncio
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from cache.cache_types import GameCache
from keyboards.inline.keypads.to_bot import get_to_bot_kb
from services.play import (
    sum_up_after_night,
    confirm_final_aim,
    sum_up_after_voting,
)
from services.mailing import MailerToPlayers

from states.states import GameFsm
from utils.utils import get_profiles, clear_data_after_all_actions


async def start_night(
    bot: Bot,
    dispatcher: Dispatcher,
    state: FSMContext,
    chat_id: int,
    scheduler: AsyncIOScheduler,
):
    game_data: GameCache = await state.get_data()
    game_data["number_of_night"] += 1
    profiles = get_profiles(
        live_players_ids=game_data["players_ids"],
        players=game_data["players"],
    )
    await state.set_data(game_data)
    await bot.send_message(
        chat_id=chat_id,
        text=f"Наступает ночь {game_data['number_of_night']}.\n\nЖивые участники:{profiles}",
        reply_markup=get_to_bot_kb("Действовать!"),
    )
    mailer = MailerToPlayers(
        state=state,
        bot=bot,
        dispatcher=dispatcher,
        group_chat_id=chat_id,
    )
    if game_data["mafias"]:
        await mailer.mail_mafia()
    if game_data["doctors"]:
        await mailer.mail_doctor()
    if game_data["policeman"]:
        await mailer.mail_policeman()
    scheduler.add_job(
        sum_up_after_night,
        "date",
        run_date=datetime.now() + timedelta(seconds=20),
        kwargs={
            "bot": bot,
            "state": state,
            "dispatcher": dispatcher,
        },
    )
    scheduler.add_job(
        mailer.suggest_vote,
        "date",
        run_date=datetime.now() + timedelta(seconds=40),
    )
    scheduler.add_job(
        confirm_final_aim,
        "date",
        run_date=datetime.now() + timedelta(seconds=50),
        kwargs={
            "bot": bot,
            "state": state,
            "group_chat_id": chat_id,
        },
    )
    scheduler.add_job(
        sum_up_after_voting,
        "date",
        run_date=datetime.now() + timedelta(seconds=60),
        kwargs={"bot": bot, "state": state},
    )
    await asyncio.sleep(62)
    await clear_data_after_all_actions(state=state)


async def start_game(
    chat_id: int,
    message_id: int,
    bot: Bot,
    state: FSMContext,
    dispatcher: Dispatcher,
    scheduler: AsyncIOScheduler,
):
    await bot.delete_message(
        chat_id=chat_id,
        message_id=message_id,
    )
    await state.set_state(GameFsm.STARTED)
    await bot.send_message(
        chat_id=chat_id,
        text="Игра начинается!",
        reply_markup=get_to_bot_kb(),
    )
    while True:
        game_data: GameCache = await state.get_data()
        if (
            not game_data["mafias"]
            or len(game_data["players_ids"]) == 1
        ):
            await bot.send_message(
                chat_id=chat_id, text="Игра завершена!"
            )
            await state.clear()
            return
        await start_night(
            bot=bot,
            dispatcher=dispatcher,
            state=state,
            chat_id=chat_id,
            scheduler=scheduler,
        )
