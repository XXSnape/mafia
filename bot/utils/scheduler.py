import asyncio
from datetime import datetime

from aiogram import Dispatcher, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telebot.types import BotName

from cache.cache_types import GameCache
from services.game.pipeline_game import Game
from utils.tg import (
    clear_game_data,
)
from utils.utils import make_build


async def start_game(
    bot: Bot,
    state: FSMContext,
    dispatcher: Dispatcher,
    scheduler: AsyncIOScheduler,
):
    game_data: GameCache = await state.get_data()
    clearing_tasks_on_schedule(
        scheduler=scheduler,
        game_chat=game_data["game_chat"],
        need_to_clean_start=False,
    )
    if len(game_data["players_ids"]) < 4:
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


def get_minutes_and_seconds_text(now: int, end_of_registration: int):
    diff = end_of_registration - now
    minutes = diff // 60
    seconds = diff % 60
    message = "До начала игры осталось примерно "
    if minutes:
        message += f"{minutes} м. "
    message += f"{seconds} с!"
    return message


async def remind_of_beginning_of_game(bot: Bot, state: FSMContext):
    game_data: GameCache = await state.get_data()
    now = int(datetime.utcnow().timestamp())
    end_of_registration = game_data["end_of_registration"]
    message = get_minutes_and_seconds_text(
        now=now, end_of_registration=end_of_registration
    )
    await bot.send_message(
        chat_id=game_data["game_chat"], text=make_build(message)
    )
