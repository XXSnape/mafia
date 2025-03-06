from aiogram import Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from cache.cache_types import (
    UserCache,
    GameCache,
    UserGameCache,
    UsersInGame,
    LivePlayersIds,
)
from states.states import GameFsm
from utils.utils import (
    get_profile_link,
    get_state_and_assign,
)


async def init_game(message: Message, state: FSMContext):
    game_data: GameCache = {
        "game_chat": message.chat.id,
        "owner": message.from_user.id,
        "pros": [],
        "cons": [],
        "players_ids": [],
        "players": {},
        "prosecutors": [],
        "mafias": [],
        "doctors": [],
        "policeman": [],
        "lucky_guys": [],
        "bodyguards": [],
        "civilians": [],
        "lawyers": [],
        "masochists": [],
        "suicide_bombers": [],
        "winners": [],
        "losers": [],
        "angels_of_death": [],
        "to_delete": [],
        "vote_for": [],
        "prime_ministers": [],
        "instigators": [],
        "angels_died": [],
        "killed_by_mafia": [],
        "killed_by_don": [],
        "punishers": [],
        "journalists": [],
        "talked": [],
        "tracking": {},
        "agents": [],
        "tracked": [],
        "killed_by_policeman": [],
        "killed_by_angel_of_death": [],
        "treated_by_doctor": [],
        "treated_by_bodyguard": [],
        "voted_by_prime": [],
        "self_protected": [],
        "have_alibi": [],
        "cant_vote": [],
        "missed": [],
        "analysts": [],
        "predicted": [],
        "sleepers": [],
        "killers": [],
        "killed_by_killer": [],
        "cancelled": [],
        "last_treated_by_doctor": {},
        "last_arrested_by_prosecutor": {},
        "last_forgiven_by_lawyer": {},
        "last_self_protected_by_bodyguard": {},
        "last_tracked_by_agent": {},
        "last_asleep_by_sleeper": {},
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
