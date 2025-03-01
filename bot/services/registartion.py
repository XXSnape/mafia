from random import shuffle
from typing import NamedTuple

from aiogram import Dispatcher, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import Message, CallbackQuery

from cache.cache_types import (
    UserCache,
    GameCache,
    UserGameCache,
    UsersInGame,
    Roles,
    LivePlayersIds,
)
from states.states import GameFsm
from utils.utils import get_profile_link


async def init_game(message: Message, state: FSMContext):
    game_data: GameCache = {
        "game_chat": message.chat.id,
        "owner": message.from_user.id,
        "players_ids": [],
        "players": {},
        "to_delete": [],
        # 'wait_for': [],
        "number_of_night": 0,
        "mafias": [],
        "doctors": [],
        "policeman": [],
        "civilians": [],
        "died": [],
        "recovered": [],
        "last_treated": 0,
    }
    await state.set_data(game_data)
    await state.set_state(GameFsm.REGISTRATION)


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


async def add_user_to_game(
    dispatcher: Dispatcher,
    tg_obj: CallbackQuery | Message,
    state: FSMContext,
) -> tuple[LivePlayersIds, UsersInGame]:
    if isinstance(tg_obj, CallbackQuery):
        chat_id = tg_obj.message.chat.id
    else:
        chat_id = tg_obj.chat.id
    user_state: FSMContext = await get_state_and_assign(
        dispatcher=dispatcher,
        chat_id=tg_obj.from_user.id,
        bot_id=tg_obj.bot.id,
    )
    user_data: UserCache = {"game_chat": chat_id}
    await user_state.update_data(user_data)
    game_data: GameCache = await state.get_data()
    user_game_data: UserGameCache = {
        "full_name": tg_obj.from_user.full_name,
        "url": get_profile_link(
            user_id=tg_obj.from_user.id,
            full_name=tg_obj.from_user.full_name,
        ),
    }
    game_data["players_ids"].append(tg_obj.from_user.id)
    game_data["players"][str(tg_obj.from_user.id)] = user_game_data
    return game_data["players_ids"], game_data["players"]


class Role(NamedTuple):
    players: list[int]
    role: str


async def select_roles(bot: Bot, state: FSMContext):
    game_data: GameCache = await state.get_data()
    ids = game_data["players_ids"][:]
    shuffle(ids)
    mafias = Role(game_data["mafias"], Roles.mafia)
    doctors = Role(game_data["doctors"], Roles.doctor)
    policeman = Role(game_data["policeman"], Roles.policeman)
    civilians = Role(game_data["civilians"], Roles.civilian)
    roles = (mafias, doctors, policeman, civilians)
    for index, user_id in enumerate(ids):
        current_role: Role = roles[index]
        game_data["players"][str(user_id)][
            "role"
        ] = current_role.role
        current_role.players.append(user_id)
    await state.set_data(game_data)
