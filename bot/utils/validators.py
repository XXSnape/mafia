from collections.abc import Callable
from functools import partial, wraps
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.roles import GameCache, PlayersIds
    from services.roles.base import Role


def get_object_id_if_exists(async_func: Callable):
    @wraps(async_func)
    async def wrapper(role: "Role", *args, **kwargs):
        game_data: GameCache = await role.state.get_data()
        players = game_data.get(role.roles_key)
        if not players:
            return
        processed_users = game_data[role.processed_users_key]
        if not processed_users:
            return
        return await async_func(
            role, *args, **kwargs, user_id=processed_users[0]
        )

    return wrapper


def remind_commissioner_about_inspections(
    game_data: "GameCache",
) -> str:
    if not game_data["text_about_checks"]:
        return "Роли ещё неизвестны"
    return (
        "По результатам прошлых проверок выяснено:\n\n"
        + game_data["text_about_checks"]
    )


def are_not_sleeping(
    game_data: "GameCache", key: str, is_equal: bool
) -> "PlayersIds":
    if is_equal:
        if game_data["number_of_night"] % 2 == 0:
            return game_data[key]
        return []
    if game_data["number_of_night"] % 2 != 0:
        return game_data[key]
    return []


are_not_sleeping_killers = partial(
    are_not_sleeping, key="killers", is_equal=False
)
are_not_sleeping_traits = partial(
    are_not_sleeping, key="traitors", is_equal=True
)


def is_4_at_night(game_data: "GameCache") -> "PlayersIds":
    if game_data["number_of_night"] == 4:
        return game_data["werewolves"]
    return []


def angel_died_2_nights_ago_or_earlier(game_data: "GameCache"):
    current_number = game_data["number_of_night"]
    angels = []
    for angel_id in game_data["angels_died"]:
        if (
            current_number
            - game_data["players"][str(angel_id)][
                "number_died_at_night"
            ]
        ) in (1, 2):
            angels.append(angel_id)
    return angels
