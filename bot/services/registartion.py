from random import shuffle
from typing import Dict, NamedTuple

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
)
from states.states import UserFsm, GameFsm


async def init_game(message: Message, state: FSMContext):
    game_data: GameCache = {
        "owner": message.from_user.id,
        "players_ids": [],
        "players": {},
        # "to_delete": [],
        "number_of_night": 0,
    }
    await state.set_data(game_data)
    await state.set_state(GameFsm.REGISTRATION)


async def get_state_and_assign(
    dispatcher: Dispatcher,
    chat_id: int,
    bot_id: int,
    new_state: State | None = None,
):
    user_state: FSMContext = FSMContext(
        storage=dispatcher.storage,
        key=StorageKey(
            chat_id=chat_id,
            user_id=chat_id,
            bot_id=bot_id,
        ),
    )
    if new_state:
        await user_state.set_state(new_state)
    return user_state


async def add_user_to_game(
    dispatcher: Dispatcher,
    tg_obj: CallbackQuery | Message,
    state: FSMContext,
) -> UsersInGame:
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
        "full_name": tg_obj.from_user.full_name
    }
    game_data["players_ids"].append(tg_obj.from_user.id)
    game_data["players"][str(tg_obj.from_user.id)] = user_game_data
    return game_data["players"]


class Roles(NamedTuple):
    mafias: list[int]
    doctors: list[int]
    policeman: list[int]
    civilians: list[int]


async def mail_mafia(
    dispatcher: Dispatcher,
    bot: Bot,
    state: FSMContext,
):
    game_data: GameCache = await state.get_data()
    mafias = game_data["mafias"]
    mafia_id = mafias[0]
    players = game_data["players"]
    options = [
        data["full_name"]
        for player_id, data in players.items()
        if int(player_id) != mafia_id
    ]
    poll = await bot.send_poll(
        chat_id=mafia_id,
        question="Кого убить этой ночью?",
        options=options,
        is_anonymous=False,
    )
    game_data["mafia_poll_delete"] = poll.message_id
    await state.set_data(game_data)
    print("set", await state.get_data())
    await get_state_and_assign(
        dispatcher=dispatcher,
        chat_id=mafia_id,
        bot_id=bot.id,
        new_state=UserFsm.MAFIA_ATTACK,
    )


async def select_roles(bot: Bot, state: FSMContext):
    game_cache: GameCache = await state.get_data()
    ids = game_cache["players_ids"][:]
    shuffle(ids)
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
    for user_id in mafias:
        await bot.send_message(
            chat_id=user_id,
            text="Твоя роль - мафия! Тебе нужно уничтожить всех горожан.",
        )
    for user_id in doctors:
        await bot.send_message(
            chat_id=user_id,
            text="Твоя роль - доктор! Тебе нужно стараться лечить тех, кому нужна помощь.",
        )
    for user_id in policeman:
        await bot.send_message(
            chat_id=user_id,
            text="Твоя роль - Комиссар! Тебе нужно вычислить мафию.",
        )
    for user_id in civilians:
        await bot.send_message(
            chat_id=user_id,
            text="Твоя роль - мирный житель! Тебе нужно вычислить мафию на голосовании.",
        )
