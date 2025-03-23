import asyncio
from collections.abc import Callable
from functools import partial, wraps
from typing import TYPE_CHECKING

from aiogram import Bot

from constants.output import NUMBER_OF_NIGHT
from utils.utils import make_pretty, get_profiles

if TYPE_CHECKING:
    from services.game.roles import GameCache, PlayersIds
    from services.game.roles.base import Role


def change_role(
    game_data: "GameCache",
    previous_role: "Role",
    new_role: "Role",
    role_key: str,
    user_id: int,
):
    game_data[previous_role.roles_key].remove(user_id)
    game_data[new_role.roles_key].append(user_id)
    game_data["players"][str(user_id)]["role"] = new_role.role
    game_data["players"][str(user_id)]["pretty_role"] = make_pretty(
        new_role.role
    )
    game_data["players"][str(user_id)]["enum_name"] = role_key
    game_data["players"][str(user_id)][
        "roles_key"
    ] = new_role.roles_key


async def notify_aliases_about_transformation(
    game_data: "GameCache",
    bot: Bot,
    new_role: "Role",
    user_id: int,
):
    url = game_data["players"][str(user_id)]["url"]
    initial_role = game_data["players"][str(user_id)]["initial_role"]
    profiles = get_profiles(
        players_ids=game_data[new_role.roles_key],
        players=game_data["players"],
        role=True,
    )
    await asyncio.gather(
        *(
            bot.send_message(
                chat_id=player_id,
                text=NUMBER_OF_NIGHT.format(
                    game_data["number_of_night"]
                )
                + f"{initial_role} {url} превратился в {make_pretty(new_role.role)}\n"
                f"Текущие союзники:\n{profiles}",
            )
            for player_id in game_data[new_role.roles_key]
        )
    )


def get_user_role_and_url(
    game_data: "GameCache",
    processed_user_id: int,
    all_roles: dict[str, "Role"],
):
    enum_name = game_data["players"][str(processed_user_id)][
        "enum_name"
    ]
    return (
        all_roles[enum_name],
        game_data["players"][str(processed_user_id)]["url"],
    )


def get_processed_role_and_user_if_exists(async_func: Callable):
    @wraps(async_func)
    async def wrapper(role: "Role", **kwargs):
        game_data: GameCache = kwargs["game_data"]
        processed_user_id = role.get_processed_user_id(game_data)
        if processed_user_id is None:
            return
        processed_role, user_url = get_user_role_and_url(
            game_data=game_data,
            processed_user_id=processed_user_id,
            all_roles=kwargs["all_roles"],
        )
        return await async_func(
            role,
            **kwargs,
            processed_role=processed_role,
            processed_user_id=processed_user_id,
            user_url=user_url,
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
