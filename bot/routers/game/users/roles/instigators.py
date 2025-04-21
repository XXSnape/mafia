from aiogram import Dispatcher, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from keyboards.inline.callback_factory.recognize_user import (
    UserActionIndexCbData,
)
from keyboards.inline.cb.cb_text import PLAYER_BACKS_CB
from services.game.saving_role_selection.instigator import (
    InstigatorSaver,
)
from states.game import UserFsm

router = Router(name=__name__)


@router.callback_query(
    UserFsm.INSTIGATOR_CHOOSES_SUBJECT,
    UserActionIndexCbData.filter(),
)
async def instigator_chooses_subject(
    callback: CallbackQuery,
    callback_data: UserActionIndexCbData,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    saver = InstigatorSaver(
        callback=callback, state=state, dispatcher=dispatcher
    )
    await saver.instigator_chooses_subject(
        callback_data=callback_data
    )


@router.callback_query(
    UserFsm.INSTIGATOR_CHOOSES_OBJECT, F.data == PLAYER_BACKS_CB
)
async def instigator_cancels_selection(
    callback: CallbackQuery,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    saver = InstigatorSaver(
        callback=callback, state=state, dispatcher=dispatcher
    )
    await saver.instigator_cancels_selection()


@router.callback_query(
    UserFsm.INSTIGATOR_CHOOSES_OBJECT, UserActionIndexCbData.filter()
)
async def instigator_chooses_object(
    callback: CallbackQuery,
    callback_data: UserActionIndexCbData,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    saver = InstigatorSaver(
        callback=callback, state=state, dispatcher=dispatcher
    )
    await saver.instigator_chooses_object(
        callback_data=callback_data
    )
