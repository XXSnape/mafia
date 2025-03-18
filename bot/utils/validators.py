from collections.abc import Callable
from functools import partial, wraps
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.roles import GameCache, PlayersIds
    from services.roles.base import Role


def get_processed_role_and_user_if_exists(async_func: Callable):
    @wraps(async_func)
    async def wrapper(role: "Role", **kwargs):
        game_data: GameCache = kwargs["game_data"]
        processed_user_id = role.get_processed_user_id(game_data)
        if processed_user_id is None:
            return
        enum_name = game_data["players"][str(processed_user_id)][
            "enum_name"
        ]
        all_roles: dict[str, Role] = kwargs["all_roles"]
        processed_role: Role = all_roles[enum_name]
        user_url = game_data["players"][str(processed_user_id)][
            "url"
        ]
        return await async_func(
            role,
            **kwargs,
            processed_role=processed_role,
            processed_user_id=processed_user_id,
            user_url=user_url
        )

    return wrapper


def get_processed_user_id_if_exists(async_func: Callable):
    @wraps(async_func)
    async def wrapper(role: "Role", **kwargs):
        game_data: GameCache = kwargs["game_data"]
        processed_user_id = role.get_processed_user_id(game_data)
        if processed_user_id is None:
            return
        return await async_func(
            role, **kwargs, processed_user_id=processed_user_id
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
