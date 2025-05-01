from collections.abc import Awaitable, Callable
from functools import wraps
from typing import TYPE_CHECKING, Concatenate

from cache.cache_types import GameCache, UserIdInt

if TYPE_CHECKING:
    from general.collection_of_roles import DataWithRoles
    from mafia.roles import RoleABC


def change_role(
    game_data: GameCache,
    previous_role: "RoleABC",
    new_role: "RoleABC",
    user_id: int,
):
    game_data[previous_role.roles_key].remove(user_id)
    game_data[new_role.roles_key].append(user_id)
    game_data["players"][str(user_id)][
        "pretty_role"
    ] = new_role.pretty_role
    game_data["players"][str(user_id)]["role_id"] = new_role.role_id
    game_data["players"][str(user_id)][
        "roles_key"
    ] = new_role.roles_key


def get_user_role_and_url(
    game_data: GameCache,
    processed_user_id: UserIdInt,
    all_roles: "DataWithRoles",
):
    role_id = game_data["players"][str(processed_user_id)]["role_id"]
    return (
        all_roles[role_id],
        game_data["players"][str(processed_user_id)]["url"],
    )


def get_processed_role_and_user_if_exists[R, **P](
    async_func: Callable[
        Concatenate["RoleABC", P], Awaitable[R | None]
    ],
):
    @wraps(async_func)
    async def wrapper(
        role: "RoleABC", **kwargs: P.kwargs
    ) -> R | None:
        game_data: GameCache = kwargs["game_data"]
        processed_user_id = role.get_processed_user_id(game_data)
        if processed_user_id is None:
            return None
        processed_role, user_url = get_user_role_and_url(
            game_data=game_data,
            processed_user_id=processed_user_id,
            all_roles=role.all_roles,
        )
        return await async_func(
            role,
            **kwargs,
            processed_role=processed_role,
            processed_user_id=processed_user_id,
            user_url=user_url,
        )

    return wrapper


def get_processed_user_id_if_exists[R, **P](
    async_func: Callable[
        Concatenate["RoleABC", P], Awaitable[R | None]
    ],
):
    @wraps(async_func)
    async def wrapper(
        role: "RoleABC", **kwargs: P.kwargs
    ) -> R | None:
        game_data: GameCache = kwargs["game_data"]
        processed_user_id = role.get_processed_user_id(game_data)
        if processed_user_id is None:
            return None
        return await async_func(
            role, **kwargs, processed_user_id=processed_user_id
        )

    return wrapper
