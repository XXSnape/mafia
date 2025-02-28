from aiogram.types import Message
from sqlalchemy.testing.suite.test_reflection import users

from cache.cache_types import UsersInGame, UserGameCache


def get_profile_link(user_id: int | str, full_name: str) -> str:
    return f'<a href="tg://user?id={user_id}">{full_name}</a>'


def get_profiles(players: UsersInGame) -> str:
    result = ""
    for index, (user_id, data) in enumerate(
        players.items(), start=1
    ):
        data: UserGameCache
        url = get_profile_link(
            user_id=user_id, full_name=data["full_name"]
        )
        result += f"\n{index}) {url}"
    return result


def get_profiles_during_registration(players: UsersInGame) -> str:
    profiles = get_profiles(players)
    return f"Скорее присоединяйся к игре!\nУчастники:\n{profiles}"
