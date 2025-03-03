from contextlib import suppress

from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.fsm.storage.base import StorageKey
from sqlalchemy.event import remove

from cache.cache_types import (
    UsersInGame,
    UserGameCache,
    LivePlayersIds,
    PlayersIds,
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


def add_voice(
    user_id: int,
    add_to: PlayersIds,
    delete_from: PlayersIds,
    prime_ministers: PlayersIds,
):
    repeat = 2 if user_id in prime_ministers else 1
    for _ in range(repeat):
        with suppress(ValueError):
            delete_from.remove(user_id)
    if user_id not in add_to:
        for _ in range(repeat):
            add_to.append(user_id)


def make_pretty(string: str) -> str:
    return f"<b><i><u>{string}</u></i></b>"


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
