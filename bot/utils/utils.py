from aiogram.types import Message
from sqlalchemy.testing.suite.test_reflection import users

from cache.cache_types import (
    UsersInGame,
    UserGameCache,
    LivePlayersIds,
)


def get_profile_link(user_id: int | str, full_name: str) -> str:
    return f'<a href="tg://user?id={user_id}">{full_name}</a>'


def get_profiles(
    live_players_ids: LivePlayersIds, players: UsersInGame
) -> str:
    result = ""

    for (
        index,
        user_id,
    ) in enumerate(live_players_ids, start=1):
        data: UserGameCache
        url = players[str(user_id)]["url"]
        result += f"\n{index}) {url}"
    return result


def get_profiles_during_registration(
    live_players_ids: LivePlayersIds, players: UsersInGame
) -> str:
    profiles = get_profiles(live_players_ids, players)
    return f"Скорее присоединяйся к игре!\nУчастники:\n{profiles}"
