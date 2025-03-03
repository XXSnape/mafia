from collections.abc import Callable
from random import randint

from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext

from cache.cache_types import (
    GameCache,
    UserGameCache,
    Groupings,
    Roles,
)
from general.exceptions import GameIsOver
from keyboards.inline.keypads.voting import get_vote_for_aim_kb
from states.states import UserFsm, GameFsm
from utils.utils import get_profiles, get_state_and_assign
import asyncio


def check_end_of_game(async_func: Callable):
    async def wrapper(**kwargs):
        result = await async_func(**kwargs)
        state = kwargs["state"]
        game_data: GameCache = await state.get_data()
        if not game_data["mafias"]:
            raise GameIsOver(winner=Groupings.civilians)
        if len(game_data["players_ids"]) == 2:
            raise GameIsOver(winner=Groupings.criminals)
        return result

    return wrapper


def remove_user_from_game(
    game_data: GameCache, user_id: int, is_night: bool
):
    if user_id in game_data["masochists"]:
        if is_night:
            game_data["losers"].append(user_id)
        else:
            game_data["winners"].append(user_id)
    if user_id in game_data["suicide_bombers"]:
        if is_night:
            game_data["winners"].append(user_id)
        else:
            game_data["losers"].append(user_id)
    game_data["players_ids"].remove(user_id)
    roles = {
        Roles.mafia: game_data["mafias"],
        Roles.doctor: game_data["doctors"],
        Roles.policeman: game_data["policeman"],
        Roles.civilian: game_data["civilians"],
        Roles.lawyer: game_data["lawyers"],
        Roles.masochist: game_data["masochists"],
        Roles.prosecutor: game_data["prosecutors"],
        Roles.lucky_gay: game_data["lucky_guys"],
        Roles.suicide_bomber: game_data["suicide_bombers"],
        Roles.bodyguard: game_data["bodyguards"],
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


@check_end_of_game
async def sum_up_after_night(
    *, bot: Bot, state: FSMContext, dispatcher: Dispatcher
):
    game_data: GameCache = await state.get_data()
    victims = (
        set(game_data["died"])
        - set(game_data["recovered"])
        - set(game_data["self_protected"])
    )
    if game_data["self_protected"]:
        if game_data["bodyguards"][0] not in game_data["recovered"]:
            victims.add(game_data["bodyguards"][0])
    text_about_dead = ""
    for victim_id in victims:
        if victim_id in game_data["lucky_guys"]:
            if randint(1, 10) in (1, 2, 3, 4):
                await bot.send_message(
                    chat_id=victim_id,
                    text="Тебе сегодня крупно повезло!",
                )
                victims.remove(victim_id)
                continue
        remove_user_from_game(
            game_data=game_data, user_id=victim_id, is_night=True
        )
        url = game_data["players"][str(victim_id)]["url"]
        role = game_data["players"][str(victim_id)]["pretty_role"]
        text_about_dead += f"Сегодня был убит {role} - {url}!\n\n"

    live_players = get_profiles(
        live_players_ids=game_data["players_ids"],
        players=game_data["players"],
    )
    text_about_dead = text_about_dead or "Сегодня ночью все выжили!"
    await bot.send_message(
        chat_id=game_data["game_chat"], text=text_about_dead
    )
    await bot.send_photo(
        chat_id=game_data["game_chat"],
        photo="https://i.pinimg.com/originals/b1/80/98/b18098074864e4b1bf5cc8412ced6421.jpg",
        caption="Живые игроки:\n" + live_players,
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
) -> bool:
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
        return False
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
    game_data["to_delete"].append(
        [group_chat_id, sent_survey.message_id]
    )
    return True


@check_end_of_game
async def sum_up_after_voting(
    *,
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

    if removed_user in game_data["have_alibi"]:
        await bot.send_message(
            chat_id=game_data["game_chat"],
            text=f"У {user_info['url']} есть алиби, поэтому местные жители отпустили гвоздя программы",
        )
        return
    remove_user_from_game(
        game_data=game_data, user_id=removed_user, is_night=False
    )
    await bot.send_message(
        chat_id=game_data["game_chat"],
        text=f'Сегодня народ принял тяжелое решение и повесил {user_info["url"]} с ролью {user_info["pretty_role"]}!',
    )


# async def check_end_of_game(state: FSMContext):
#     game_data: GameCache = await state.get_data()
#     if not game_data["mafias"]:
#         raise GameIsOver(winner=Groupings.civilians)
#     if len(game_data["players"]) == 2:
#         raise GameIsOver(winner=Groupings.criminals)
