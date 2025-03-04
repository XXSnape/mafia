from aiogram import Router, Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from cache.cache_types import Roles, UserCache, GameCache
from keyboards.inline.callback_factory.recognize_user import (
    UserActionIndexCbData,
)
from keyboards.inline.cb.cb_text import DRAW_CB
from services.actions_at_night import (
    take_action_and_register_user,
)
from states.states import UserFsm
from utils.utils import get_state_and_assign

router = Router(name=__name__)


@router.callback_query(
    UserFsm.ANALYST_ASSUMES, UserActionIndexCbData.filter()
)
async def analyst_assumes(
    callback: CallbackQuery,
    callback_data: UserActionIndexCbData,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    await take_action_and_register_user(
        callback=callback,
        callback_data=callback_data,
        state=state,
        dispatcher=dispatcher,
        role=Roles.analyst,
    )


@router.callback_query(UserFsm.ANALYST_ASSUMES, F.data == DRAW_CB)
async def analyst_assumes_draw(
    callback: CallbackQuery,
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
    game_data["predicted"].append(0)
    await callback.message.delete()
    await callback.message.answer(
        text="Ты предположил, что никого не повесят днём"
    )
    await callback.bot.send_message(
        chat_id=game_data["game_chat"],
        text=Roles.analyst.value.message_to_group_after_action,
    )
