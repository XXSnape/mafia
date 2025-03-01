from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext

from cache.cache_types import GameCache, UserGameCache
from keyboards.inline.keypads.voting import get_vote_for_aim_kb
from services.registartion import get_state_and_assign
from states.states import UserFsm, GameFsm
from utils.utils import get_profiles
import asyncio


def remove_user_from_game(game_data: GameCache, user_id: int):
    game_data["players_ids"].remove(user_id)
    roles = {
        "Мафия": game_data["mafias"],
        "Доктор": game_data["doctors"],
        "Комиссар": game_data["policeman"],
        "Мирный житель": game_data["civilians"],
    }
    user_role = game_data["players"][str(user_id)]["role"]
    roles[user_role].remove(user_id)


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
        remove_user_from_game(game_data=game_data, user_id=victim_id)
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


async def sum_up_after_voting(
    bot: Bot,
    state: FSMContext,
):
    game_data: GameCache = await state.get_data()
    pros = game_data["pros"]
    cons = game_data["cons"]
    if len(pros) == len(cons) or len(pros) < len(cons):
        await bot.send_message(
            chat_id=game_data["game_chat"],
            text=f"Что ж, такова воля народа! Сегодня днем город не опустел!",
        )
        return
    removed_user = game_data["vote_for"][0]
    user_info: UserGameCache = game_data["players"][
        str(removed_user)
    ]
    remove_user_from_game(game_data=game_data, user_id=removed_user)
    await bot.send_message(
        chat_id=game_data["game_chat"],
        text=f'Сегодня народ принял тяжелое решение и повесил {user_info["url"]}, который был {user_info["role"]}!',
    )
