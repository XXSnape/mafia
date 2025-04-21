from aiogram import Dispatcher, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from keyboards.inline.callback_factory.recognize_user import (
    CheckOrKill,
    PoliceActionIndexCbData,
)
from keyboards.inline.cb.cb_text import (
    PLAYER_BACKS_CB,
    POLICEMAN_CHECKS_CB,
    POLICEMAN_KILLS_CB,
)
from services.game.saving_role_selection.policeman import (
    PolicemanSaver,
)
from states.game import UserFsm

router = Router(name=__name__)


@router.callback_query(
    UserFsm.POLICEMAN_CHECKS,
    F.data.in_([POLICEMAN_KILLS_CB, POLICEMAN_CHECKS_CB]),
)
async def policeman_makes_choice(
    callback: CallbackQuery,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    saver = PolicemanSaver(
        callback=callback, state=state, dispatcher=dispatcher
    )
    await saver.policeman_makes_choice()


@router.callback_query(
    UserFsm.POLICEMAN_CHECKS, F.data == PLAYER_BACKS_CB
)
async def policeman_cancels_selection(
    callback: CallbackQuery,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    saver = PolicemanSaver(
        callback=callback, state=state, dispatcher=dispatcher
    )
    await saver.policeman_cancels_selection()


@router.callback_query(
    UserFsm.POLICEMAN_CHECKS,
    PoliceActionIndexCbData.filter(
        F.check_or_kill == CheckOrKill.kill
    ),
)
async def policeman_chose_to_kill(
    callback: CallbackQuery,
    callback_data: PoliceActionIndexCbData,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    saver = PolicemanSaver(
        callback=callback, state=state, dispatcher=dispatcher
    )
    await saver.policeman_chose_to_kill(callback_data=callback_data)


@router.callback_query(
    UserFsm.POLICEMAN_CHECKS,
    PoliceActionIndexCbData.filter(
        F.check_or_kill == CheckOrKill.check
    ),
)
async def policeman_chose_to_check(
    callback: CallbackQuery,
    callback_data: PoliceActionIndexCbData,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    saver = PolicemanSaver(
        callback=callback, state=state, dispatcher=dispatcher
    )
    await saver.policeman_chose_to_check(callback_data=callback_data)
