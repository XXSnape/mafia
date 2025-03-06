from aiogram import Router, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from cache.cache_types import (
    Roles,
)
from keyboards.inline.callback_factory.recognize_user import (
    UserActionIndexCbData,
)
from services.actions_at_night import (
    take_action_and_register_user,
)
from states.states import UserFsm

router = Router(name=__name__)


@router.callback_query(
    UserFsm.MAFIA_ATTACKS, UserActionIndexCbData.filter()
)
async def mafia_attacks(
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
        role=Roles.don.value.alias.role,
    )


@router.callback_query(
    UserFsm.DON_ATTACKS, UserActionIndexCbData.filter()
)
async def don_attacks(
    callback: CallbackQuery,
    callback_data: UserActionIndexCbData,
    state: FSMContext,
    dispatcher: Dispatcher,
):

    game_data, user_id = await take_action_and_register_user(
        callback=callback,
        callback_data=callback_data,
        state=state,
        dispatcher=dispatcher,
        role=Roles.don,
    )
    game_data["killed_by_don"].append(user_id)
