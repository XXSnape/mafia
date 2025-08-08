import datetime
from contextlib import suppress

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.context import FSMContext
from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from cache.cache_types import GameCache
from faststream.rabbit import RabbitBroker
from general import settings
from keyboards.inline.keypads.join import remind_about_joining_kb
from sqlalchemy.ext.asyncio import AsyncSession
from utils.pretty_text import (
    get_minutes_and_seconds_text,
    make_build,
)
from utils.state import clear_game_data

from mafia.pipeline_game import Game


async def start_game(
    bot: Bot,
    state: FSMContext,
    dispatcher: Dispatcher,
    scheduler: AsyncIOScheduler,
    session: AsyncSession,
    broker: RabbitBroker,
):
    game_data: GameCache = await state.get_data()
    clearing_tasks_on_schedule(
        scheduler=scheduler,
        game_chat=game_data["game_chat"],
        need_to_clean_start=False,
    )
    if (
        len(game_data["live_players_ids"])
        < settings.mafia.minimum_number_of_players
    ):
        await clear_game_data(
            game_data=game_data,
            bot=bot,
            dispatcher=dispatcher,
            state=state,
            message_id=game_data["start_message_id"],
        )
        with suppress(TelegramAPIError):
            await bot.send_message(
                chat_id=game_data["game_chat"],
                text=make_build(
                    f"😢Недостаточно игроков для начала игры! Нужно минимум "
                    f"{settings.mafia.minimum_number_of_players}. Игра отменяется."
                ),
            ),
        return

    game = Game(
        bot=bot,
        group_chat_id=game_data["game_chat"],
        state=state,
        dispatcher=dispatcher,
        broker=broker,
        session=session,
    )
    await game.start_game()


def clearing_tasks_on_schedule(
    scheduler: AsyncIOScheduler,
    game_chat: int,
    need_to_clean_start: bool,
):
    if need_to_clean_start is True:
        with suppress(JobLookupError):
            scheduler.remove_job(job_id=f"start_{game_chat}")
    with suppress(JobLookupError):
        scheduler.remove_job(job_id=f"remind_{game_chat}")


async def remind_of_beginning_of_game(bot: Bot, state: FSMContext):
    game_data: GameCache = await state.get_data()
    now = int(datetime.datetime.now(datetime.UTC).timestamp())
    end_of_registration = game_data["end_of_registration"]
    message = get_minutes_and_seconds_text(
        start=now, end=end_of_registration
    )
    kb = await remind_about_joining_kb(
        bot=bot,
        game_chat=game_data["game_chat"],
    )
    with suppress(TelegramAPIError):
        await bot.send_message(
            chat_id=game_data["game_chat"],
            text=make_build(message),
            reply_markup=kb,
        )
