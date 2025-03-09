import asyncio

from aiogram import Dispatcher, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from general.collection_of_roles import Roles
from services.roles import Traitor, Mafia
from cache.cache_types import GameCache, UserCache
from keyboards.inline.callback_factory.recognize_user import (
    UserActionIndexCbData,
)
from states.states import UserFsm
from utils.utils import get_state_and_assign, make_pretty

router = Router(name=__name__)


@router.callback_query(
    UserFsm.TRAITOR_FINDS_OUT,
    UserActionIndexCbData.filter(),
)
async def traitor_finds_out(
    callback: CallbackQuery,
    callback_data: UserActionIndexCbData,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    user_data: UserCache = await state.get_data()
    game_state = await get_state_and_assign(
        dispatcher=dispatcher,
        chat_id=user_data["game_chat"],
        bot_id=callback.bot.id,
    )
    game_data: GameCache = await game_state.get_data()
    user_id = game_data["players_ids"][callback_data.user_index]
    url = game_data["players"][str(user_id)]["url"]
    role = game_data["players"][str(user_id)]["pretty_role"]
    await callback.message.delete()
    await callback.bot.send_message(
        chat_id=game_data["game_chat"],
        text=Traitor.message_to_group_after_action,
    )
    await callback.message.answer(
        text=Traitor.message_to_user_after_action.format(url=url)
    )
    await asyncio.gather(
        *(
            callback.bot.send_message(
                chat_id=player_id,
                text=f"{make_pretty(Roles.traitor.value.role)} проверил и узнал, что {url} - {role}",
            )
            for player_id in game_data[Mafia.roles_key]
            + game_data[Traitor.roles_key]
        )
    )
