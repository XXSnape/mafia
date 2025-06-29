from aiogram import Dispatcher, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from keyboards.inline.callback_factory.recognize_user import (
    UserActionIndexCbData,
)
from keyboards.inline.cb.cb_text import PLAYER_BACKS_CB
from services.game.saving_role_selection.forger import ForgerSaver
from states.game import UserFsm

router = Router(name=__name__)


@router.callback_query(
    UserFsm.FORGER, UserActionIndexCbData.filter()
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


@router.callback_query(UserFsm.FORGER, F.data == PLAYER_BACKS_CB)
async def forger_cancels_selection(
    callback: CallbackQuery,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    saver = ForgerSaver(
        callback=callback, state=state, dispatcher=dispatcher
    )
    await saver.forger_cancels_selection()


@router.callback_query(UserFsm.FORGER, F.data)
async def forger_selects_documents(
    callback: CallbackQuery,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    saver = ForgerSaver(
        callback=callback, state=state, dispatcher=dispatcher
    )
    await saver.forger_selects_documents()
