from aiogram import Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from cache.cache_types import (
    GameCache,
    LivePlayersIds,
    UserCache,
    UserGameCache,
    UsersInGame,
)
from states.states import GameFsm
from utils.utils import get_profile_link, get_state_and_assign


async def init_game(message: Message, state: FSMContext):
    game_data: GameCache = {
        "game_chat": message.chat.id,
        "owner": message.from_user.id,
        "pros": [],
        "cons": [],
        "players_ids": [],
        "players": {},
        "messages_after_night": [],
        "winners": [],
        "losers": [],
        "to_delete": [],
        "vote_for": [],
        "tracking": {},
        "text_about_checks": "",
        # 'wait_for': [],
        "number_of_night": 0,
    }
    await state.set_data(game_data)
    await state.set_state(GameFsm.REGISTRATION)


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
