from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext

from cache.cache_types import GameCache
from keyboards.inline.keypads.voting import get_vote_for_aim_kb
from services.registartion import get_state_and_assign
from states.states import UserFsm, GameFsm
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


async def confirm_final_aim(
    bot: Bot, state: FSMContext, group_chat_id: int
):
    game_data: GameCache = await state.get_data()
    vote_for = game_data["vote_for"]
    vote_for.sort(reverse=True)

    if (not vote_for) or (
        len(vote_for) != 1
        and vote_for.count(vote_for[0])
        == vote_for.count(vote_for[1])
    ):
        await bot.send_message(
            chat_id=group_chat_id,
            text="Доброта или банальная несогласованность? "
            "Посмотрим, воспользуются ли преступники таким подарком.",
        )
        return
    aim_id = vote_for[0]
    vote_for.clear()
    url = game_data["players"][str(aim_id)]["url"]
    await state.set_state(GameFsm.VOTE)
    sent_survey = await bot.send_message(
        chat_id=group_chat_id,
        text=f"На кону судьба {url}!",
        reply_markup=get_vote_for_aim_kb(
            user_id=aim_id,
            pros=game_data["pros"],
            cons=game_data["cons"],
        ),
    )
    game_data["to_delete"].append(sent_survey.message_id)
