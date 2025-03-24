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
    delete_messages_from_to_delete,
    reset_user_state,
    reset_state_to_all_users,
    clear_game_data,
)
from utils.utils import make_build


async def start_game(
    message: Message,
    state: FSMContext,
    dispatcher: Dispatcher,
    scheduler: AsyncIOScheduler,
):
    clearing_tasks_on_schedule(
        scheduler=scheduler,
        game_chat=message.chat.id,
        need_to_clean_start=False,
    )
    game_data: GameCache = await state.get_data()
    if len(game_data["players_ids"]) < 4:
        await clear_game_data(
            game_data=game_data,
            bot=message.bot,
            dispatcher=dispatcher,
            state=state,
            message_id=message.message_id,
        )
        await message.answer(
            text=make_build(
                "Недостаточно игроков для начала игры! Нужно минимум 4. Игра отменяется."
            )
        ),
        return

    game = Game(
        message=message,
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
