from aiogram import Dispatcher, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from keyboards.inline.callback_factory.recognize_user import (
    UserActionIndexCbData,
)
from services.actions_at_night import take_action_and_register_user
from states.states import UserFsm

router = Router(name=__name__)


@router.callback_query(
    StateFilter(
        UserFsm.AGENT_WATCHES,
        UserFsm.ANALYST_ASSUMES,
        UserFsm.ANGEL_TAKES_REVENGE,
        UserFsm.BODYGUARD_PROTECTS,
        UserFsm.DOCTOR_TREATS,
        UserFsm.INSTIGATOR_LYING,
        UserFsm.JOURNALIST_TAKES_INTERVIEW,
        UserFsm.KILLER_ATTACKS,
        UserFsm.LAWYER_PROTECTS,
        UserFsm.MAFIA_ATTACKS,
        UserFsm.CLOFFELINE_GIRL_PUTS_TO_SLEEP,
        UserFsm.PROSECUTOR_ARRESTS,
    ),
    UserActionIndexCbData.filter(),
)
async def handle_action(
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
    )
