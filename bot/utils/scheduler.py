import asyncio
from datetime import datetime

from aiogram import Dispatcher, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telebot.types import BotName

from cache.cache_types import GameCache
from services.game.pipeline_game import Game
from utils.tg import delete_messages_from_to_delete, reset_user_state
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
        is_running_on_schedule=True,
    )
    game_data: GameCache = await state.get_data()
    if len(game_data["players_ids"]) < 4:
        await message.delete()
        await delete_messages_from_to_delete(
            bot=message.bot,
            to_delete=game_data["to_delete"],
            state=None,
        )
        await asyncio.gather(
            *(
                [
                    reset_user_state(
                        dispatcher=dispatcher,
                        user_id=user_id,
                        bot_id=message.bot.id,
                    )
                    for user_id in game_data["players_ids"]
                ]
            )
        )
        await message.answer(
            text=make_build(
                "Недостаточно игроков для начала игры! Нужно минимум 4. Игра отменяется."
            )
        ),
        await state.clear(),
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
    is_running_on_schedule: bool,
):
    if is_running_on_schedule is False:
        scheduler.remove_job(job_id=f"start_{game_chat}")
    scheduler.remove_job(job_id=f"remind_{game_chat}")


async def remind_of_beginning_of_game(bot: Bot, state: FSMContext):
    game_data: GameCache = await state.get_data()
    now = int(datetime.utcnow().timestamp())
    end_of_registration = game_data["end_of_registration"]
    diff = end_of_registration - now
    minutes = diff // 60
    seconds = diff % 60
    message = "До начала игры осталось примерно "
    if minutes:
        message += f"{minutes} минут "
    message += f"{seconds} секунд!"
    await bot.send_message(
        chat_id=game_data["game_chat"], text=make_build(message)
    )
