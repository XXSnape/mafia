from aiogram import Dispatcher, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from keyboards.inline.callback_factory.recognize_user import (
    UserActionIndexCbData,
)
from keyboards.inline.cb.cb_text import (
    PLAYER_BACKS_CB,
    POISONER_POISONS_CB,
    POLICEMAN_KILLS_CB,
)
from services.game.saving_role_selection.poisoner import (
    PoisonerSaver,
)
from states.game import UserFsm

router = Router(name=__name__)


@router.callback_query(
    UserFsm.POISONER_CHOOSES_ACTION, F.data == POLICEMAN_KILLS_CB
)
async def poisoner_chose_to_kill(
    callback: CallbackQuery,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    saver = PoisonerSaver(
        callback=callback, state=state, dispatcher=dispatcher
    )
    await saver.poisoner_chose_to_kill()


@router.callback_query(
    UserFsm.POISONER_CHOOSES_ACTION, F.data == POISONER_POISONS_CB
)
async def poisoner_poisons(
    callback: CallbackQuery,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    saver = PoisonerSaver(
        callback=callback, state=state, dispatcher=dispatcher
    )
    await saver.poisoner_poisons()


@router.callback_query(
    UserFsm.POISONER_CHOSE_TO_KILL, F.data == PLAYER_BACKS_CB
)
async def poisoner_cancels_selection(
    callback: CallbackQuery,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    saver = PoisonerSaver(
        callback=callback, state=state, dispatcher=dispatcher
    )
    await saver.poisoner_cancels_selection()


@router.callback_query(
    UserFsm.POISONER_CHOSE_TO_KILL,
    UserActionIndexCbData.filter(),
)
async def poisoner_chose_victim(
    callback: CallbackQuery,
    callback_data: UserActionIndexCbData,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    saver = PoisonerSaver(
        callback=callback, state=state, dispatcher=dispatcher
    )
    await saver.poisoner_chose_victim(callback_data=callback_data)
