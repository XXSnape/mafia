from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from faststream.rabbit import RabbitBroker
from sqlalchemy.ext.asyncio import AsyncSession

from cache.cache_types import GameCache
from services.game.pipeline_game import Game
from utils.state import clear_game_data
from utils.pretty_text import (
    make_build,
    get_minutes_and_seconds_text,
)


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
    if len(game_data["live_players_ids"]) < 4:
        await clear_game_data(
            game_data=game_data,
            bot=bot,
            dispatcher=dispatcher,
            state=state,
            message_id=game_data["start_message_id"],
        )
        await bot.send_message(
            chat_id=game_data["game_chat"],
            text=make_build(
                "Недостаточно игроков для начала игры! Нужно минимум 4. Игра отменяется."
            ),
        ),
        return

    game = Game(
        bot=bot,
        group_chat_id=game_data["game_chat"],
        state=state,
        dispatcher=dispatcher,
        scheduler=scheduler,
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
        scheduler.remove_job(job_id=f"start_{game_chat}")
    scheduler.remove_job(job_id=f"remind_{game_chat}")


async def remind_of_beginning_of_game(bot: Bot, state: FSMContext):
    game_data: GameCache = await state.get_data()
    now = int(datetime.utcnow().timestamp())
    end_of_registration = game_data["end_of_registration"]
    message = get_minutes_and_seconds_text(
        start=now, end=end_of_registration
    )
    await bot.send_message(
        chat_id=game_data["game_chat"], text=make_build(message)
    )
