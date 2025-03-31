from aiogram import Dispatcher, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from keyboards.inline.callback_factory.recognize_user import (
    UserActionIndexCbData,
)
from keyboards.inline.cb.cb_text import PLAYER_BACKS_CB
from services.game.saving_role_selection.forger import ForgerSaver
from states.states import UserFsm

router = Router(name=__name__)


@router.callback_query(
    UserFsm.FORGER_FAKES, UserActionIndexCbData.filter()
)
async def forger_fakes(
    callback: CallbackQuery,
    callback_data: UserActionIndexCbData,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    saver = ForgerSaver(
        callback=callback, state=state, dispatcher=dispatcher
    )
    await saver.forger_fakes(callback_data=callback_data)


@router.callback_query(
    UserFsm.FORGER_FAKES, F.data == PLAYER_BACKS_CB
)
async def forges_cancels_selection(
    callback: CallbackQuery,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    saver = ForgerSaver(
        callback=callback, state=state, dispatcher=dispatcher
    )
    await saver.forges_cancels_selection()


@router.callback_query(UserFsm.FORGER_FAKES, F.data)
async def forges_selects_documents(
    callback: CallbackQuery,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    saver = ForgerSaver(
        callback=callback, state=state, dispatcher=dispatcher
    )
    await saver.forges_selects_documents()
