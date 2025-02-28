from typing import Dict, NamedTuple

from aiogram import Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import Message, CallbackQuery

from cache.cache_types import (
    UserCache,
    GameCache,
    UserGameCache,
    UsersInGame,
)


async def add_user_to_game(
    dispatcher: Dispatcher,
    tg_obj: CallbackQuery | Message,
    state: FSMContext,
) -> UsersInGame:
    if isinstance(tg_obj, CallbackQuery):
        chat_id = tg_obj.message.chat.id
    else:
        chat_id = tg_obj.chat.id
    user_state: FSMContext = FSMContext(
        storage=dispatcher.storage,
        key=StorageKey(
            chat_id=tg_obj.from_user.id,
            user_id=tg_obj.from_user.id,
            bot_id=tg_obj.bot.id,
        ),
    )
    user_data: UserCache = {"game_chat": chat_id}
    await user_state.update_data(user_data)
    game_data: GameCache = await state.get_data()
    user_game_data: UserGameCache = {
        "full_name": tg_obj.from_user.full_name
    }
    if not game_data:
        game_data: GameCache = {
            "owner": tg_obj.from_user.id,
            "players_ids": [tg_obj.from_user.id],
            "players": {str(tg_obj.from_user.id): user_game_data},
        }
        await state.update_data(game_data)
    else:
        game_data["players_ids"].append(tg_obj.from_user.id)
        game_data["players"][
            str(tg_obj.from_user.id)
        ] = user_game_data
    return game_data["players"]


class Roles(NamedTuple):
    mafias: list[int]
    doctors: list[int]
    policeman: list[int]
    civilians: list[int]


async def select_roles(state: FSMContext):
    game_cache: GameCache = await state.get_data()
    ids = game_cache["players_ids"][:]
    mafias = []
    doctors = []
    policeman = []
    civilians = []
    roles = Roles(mafias, doctors, policeman, civilians)
    for index, user_id in enumerate(ids):
        roles[index].append(user_id)
    await state.update_data(
        {
            "mafias": mafias,
            "doctors": doctors,
            "policeman": policeman,
            "died": [],
        }
    )
