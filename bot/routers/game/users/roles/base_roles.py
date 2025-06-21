from aiogram import Dispatcher, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from keyboards.inline.callback_factory.recognize_user import (
    UserActionIndexCbData,
)
from services.game.game_assistants import (
    take_action_and_save_data,
)
from states.game import UserFsm

router = Router(name=__name__)


@router.callback_query(
    StateFilter(
        UserFsm.BASIC_NIGHT_ROLE,
        UserFsm.BASIC_ROLE_WITH_ALLIES,
    ),
    UserActionIndexCbData.filter(),
)
async def handle_action(
    callback: CallbackQuery,
    callback_data: UserActionIndexCbData,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    await take_action_and_save_data(
        callback=callback,
        callback_data=callback_data,
        state=state,
        dispatcher=dispatcher,
    )
