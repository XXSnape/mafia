from collections import Counter
from contextlib import suppress
from inspect import get_annotations
from typing import TYPE_CHECKING
from collections.abc import Callable
from aiogram import Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.fsm.storage.base import StorageKey
from collections import defaultdict
from cache.cache_types import GameCache, UserIdInt
from constants.output import MONEY_SYM

if TYPE_CHECKING:
    from services.roles.base import Role
    from services.roles import (
        LivePlayersIds,
        PlayersIds,
        UserGameCache,
        UsersInGame,
    )


def dependency_injection(func: Callable, data: dict):
    keys = set(get_annotations(func).keys())
    suitable_keys = keys & set(data.keys())
    return {
        key: val for key, val in data.items() if key in suitable_keys
    }


def get_profile_link(user_id: int | str, full_name: str) -> str:
    return f'<a href="tg://user?id={user_id}">{full_name}</a>'


def get_profiles(
    players_ids: "LivePlayersIds",
    players: "UsersInGame",
    role: bool = False,
    initial_role: bool = False,
    money_need: bool = False,
) -> str:
    result = ""

    for (
        index,
        user_id,
    ) in enumerate(players_ids, start=1):
        url = players[str(user_id)]["url"]
        if role:
            if initial_role:
                role = players[str(user_id)]["initial_role"]
            else:
                role = players[str(user_id)]["pretty_role"]
            if money_need:
                money = players[str(user_id)]["money"]
                result += (
                    f"\n{index}) {url} - {role} ({money}{MONEY_SYM})"
                )
            else:
                result += f"\n{index}) {url} - {role}"
        else:
            result += f"\n{index}) {url}"
    return result


def get_profiles_during_registration(
    live_players_ids: "LivePlayersIds", players: "UsersInGame"
) -> str:
    profiles = get_profiles(live_players_ids, players)
    return f"Скорее присоединяйся к игре!\nУчастники:\n{profiles}"


def add_voice(
    user_id: int,
    add_to: "PlayersIds",
    delete_from: "PlayersIds",
    prime_ministers: "PlayersIds",
):
    repeat = 2 if user_id in prime_ministers else 1
    for _ in range(repeat):
        with suppress(ValueError):
            delete_from.remove(user_id)
    if user_id not in add_to:
        for _ in range(repeat):
            add_to.append(user_id)


def make_build(string: str) -> str:
    return f"<b>{string}</b>"


def make_pretty(string: str) -> str:
    return f"<b><i><u>{string}</u></i></b>"


def get_results_of_goal_identification(game_data: GameCache):
    def sorting_by_voting(voting_data):
        return len(voting_data[1])

    result = make_build(
        f"❗️Результаты голосования дня {game_data['number_of_night']}:"
    )

    vote_for = game_data["vote_for"]
    voting = defaultdict(list)
    for voting_id, voted_id in vote_for:
        voting[game_data["players"][str(voted_id)]["url"]].append(
            game_data["players"][str(voting_id)]["url"]
        )

    result_voting = ""
    if not voting:
        result_voting = make_build(
            "\n\n😯Сегодня нет потенциальных жертв!"
        )
        return result + result_voting
    for voted, voting_people in sorted(
        voting.items(), key=sorting_by_voting, reverse=True
    ):
        result_voting += (
            f"\n\n📝Голосовавшие за {voted} ({len(voting_people)}):\n● "
            + "\n● ".join(
                voting_person for voting_person in voting_people
            )
        )
    return result + result_voting


def get_results_of_voting(
    game_data: GameCache, removed_user_id: UserIdInt
):
    if not removed_user_id:
        return make_build(
            "Доброта или банальная несогласованность? Посмотрим, воспользуются ли преступники таким подарком."
        )

    user_url = game_data["players"][str(removed_user_id)]["url"]
    pros = len(game_data["pros"])
    cons = len(game_data["cons"])
    return (
        make_build(f"Подводим итоги судьбы {user_url}:\n")
        + f"✅За линчевание - {pros} 🚫Против - {cons}\n\n"
    )


def record_accrual(
    game_data: GameCache,
    roles_key: str,
    processed_role: "Role",
    user_url: str,
    action: str,
):
    for player_id in game_data[roles_key]:
        game_data["players"][str(player_id)][
            "money"
        ] += processed_role.payment_for_treatment
        game_data["players"][str(player_id)]["achievements"].append(
            f'Ночь {game_data["number_of_night"]}. '
            f"{action} {user_url} ({processed_role.role}) - {processed_role.payment_for_treatment}💵"
        )


async def get_state_and_assign(
    dispatcher: Dispatcher,
    chat_id: int,
    bot_id: int,
    new_state: State | None = None,
):
    chat_state: FSMContext = FSMContext(
        storage=dispatcher.storage,
        key=StorageKey(
            chat_id=chat_id,
            user_id=chat_id,
            bot_id=bot_id,
        ),
    )
    if new_state:
        await chat_state.set_state(new_state)
    return chat_state


def get_the_most_frequently_encountered_id(ids: "PlayersIds"):
    if not ids:
        return None
    if len(set(ids)) == 1:
        return ids[0]
    most_common = Counter(ids).most_common()
    if most_common[0][1] == most_common[1][1]:
        return None
    return most_common[0][0]
