import asyncio
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from cache.cache_types import GameCache, Groupings
from general.exceptions import GameIsOver
from keyboards.inline.keypads.to_bot import get_to_bot_kb
from services.play import (
    sum_up_after_night,
    confirm_final_aim,
    sum_up_after_voting,
)
from services.mailing import MailerToPlayers

from states.states import GameFsm
from utils.utils import (
    get_profiles,
    clear_data_after_all_actions,
    delete_messages_from_to_delete,
)


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

    await asyncio.sleep(20)
    await delete_messages_from_to_delete(
        bot=bot, to_delete=game_data["to_delete"]
    )
    await sum_up_after_night(
        bot=bot, state=state, dispatcher=dispatcher
    )
    await asyncio.sleep(20)
    await mailer.suggest_vote()
    await asyncio.sleep(10)
    await delete_messages_from_to_delete(
        bot=bot, to_delete=game_data["to_delete"]
    )
    result = await confirm_final_aim(
        bot=bot,
        state=state,
        group_chat_id=chat_id,
    )
    if result:
        await asyncio.sleep(10)
    await delete_messages_from_to_delete(
        bot=bot, to_delete=game_data["to_delete"]
    )
    await sum_up_after_voting(
        bot=bot,
        state=state,
    )
    await asyncio.sleep(2)
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
        try:
            await start_night(
                bot=bot,
                dispatcher=dispatcher,
                state=state,
                chat_id=chat_id,
                scheduler=scheduler,
            )
        except GameIsOver as e:
            if e.winner is Groupings.criminals:
                await bot.send_message(
                    chat_id=chat_id,
                    text="Игра завершена! Местная мафия подчинила город себе!",
                )
            elif e.winner is Groupings.civilians:
                await bot.send_message(
                    chat_id=chat_id,
                    text="Игра завершена! Вся преступная верхушка обезглавлена, город может спать спокойно!",
                )
            game_data: GameCache = await state.get_data()
            await delete_messages_from_to_delete(
                bot=bot, to_delete=game_data["to_delete"]
            )
            await state.clear()
            return
