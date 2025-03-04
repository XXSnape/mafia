from aiogram import Router, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from cache.cache_types import Roles
from keyboards.inline.callback_factory.recognize_user import (
    UserActionIndexCbData,
)
from services.actions_at_night import (
    take_action_and_register_user,
)
from states.states import UserFsm

router = Router(name=__name__)


@router.callback_query(
    UserFsm.JOURNALIST_TAKES_INTERVIEW,
    UserActionIndexCbData.filter(),
)
async def journalist_takes_interview(
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
        role=Roles.journalist,
    )
