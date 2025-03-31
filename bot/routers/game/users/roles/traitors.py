from aiogram import Dispatcher, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from keyboards.inline.callback_factory.recognize_user import (
    UserActionIndexCbData,
)
from services.game.saving_role_selection.traitor import TraitorSaver
from states.states import UserFsm

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
    saver = TraitorSaver(
        callback=callback, state=state, dispatcher=dispatcher
    )
    await saver.traitor_finds_out(callback_data=callback_data)
