import asyncio
from contextlib import suppress

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.testing.suite.test_reflection import users

from cache.cache_types import (
    UsersInGame,
    UserGameCache,
    LivePlayersIds,
    PlayersIds,
    GameCache,
    ChatsAndMessagesIds,
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
    user_id: int, add_to: PlayersIds, delete_from: PlayersIds
):
    with suppress(ValueError):
        delete_from.remove(user_id)
    if user_id not in add_to:
        add_to.append(user_id)


async def delete_message_by_chat(
    bot: Bot, chat_id: int, message_id: int
):
    with suppress(TelegramBadRequest):
        await bot.delete_message(
            chat_id=chat_id, message_id=message_id
        )


async def delete_messages_from_to_delete(
    bot: Bot, to_delete: ChatsAndMessagesIds
):
    await asyncio.gather(
        *(
            delete_message_by_chat(
                bot=bot, chat_id=chat_id, message_id=message_id
            )
            for chat_id, message_id in to_delete
        )
    )


async def clear_data_after_all_actions(state: FSMContext):
    game_data: GameCache = await state.get_data()
    game_data["pros"].clear()
    game_data["cons"].clear()
    game_data["recovered"].clear()
    game_data["vote_for"].clear()
    game_data["died"].clear()
    await state.set_data(game_data)
