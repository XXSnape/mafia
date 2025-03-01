from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext

from cache.cache_types import GameCache
from services.registartion import get_state_and_assign
from states.states import UserFsm
from utils.utils import get_profiles
import asyncio


async def report_death(
    bot: Bot, chat_id: int, dispatcher: Dispatcher
):

    await get_state_and_assign(
        dispatcher=dispatcher,
        chat_id=chat_id,
        bot_id=bot.id,
        new_state=UserFsm.WAIT_FOR_LATEST_LETTER,
    )
    await bot.send_message(
        chat_id=chat_id,
        text="К сожалению, тебя убили! Отправь напоследок все, что думаешь!",
    )


async def sum_up_after_night(
    bot: Bot, state: FSMContext, dispatcher: Dispatcher
):
    game_data: GameCache = await state.get_data()
    victims = set(game_data["died"]) - set(game_data["recovered"])
    text_about_dead = ""
    for victim_id in victims:
        game_data["players_ids"].remove(victim_id)
        url = game_data["players"][str(victim_id)]["url"]
        role = game_data["players"][str(victim_id)]["role"]
        text_about_dead += f"Сегодня был убит {role} - {url}!\n\n"
    live_players = get_profiles(
        live_players_ids=game_data["players_ids"],
        players=game_data["players"],
    )
    text_about_dead = text_about_dead or "Сегодня ночью все выжили!"
    await bot.send_message(
        chat_id=game_data["game_chat"], text=text_about_dead
    )
    await bot.send_message(
        chat_id=game_data["game_chat"],
        text="Живые игроки:\n" + live_players,
    )
    if victims:
        await asyncio.gather(
            *(
                report_death(
                    bot=bot, chat_id=victim_id, dispatcher=dispatcher
                )
                for victim_id in victims
            )
        )


async def suggest_vote(bot: Bot, chat_id: int):
    await bot.send_message()
