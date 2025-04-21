from aiogram import Dispatcher, F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from services.game.processing_user_actions import UserManager
from states.game import UserFsm

router = Router(name=__name__)


@router.message(
    StateFilter(
        UserFsm.DON_ATTACKS,
        UserFsm.MAFIA_ATTACKS,
        UserFsm.TRAITOR_FINDS_OUT,
        UserFsm.FORGER_FAKES,
        UserFsm.POLICEMAN_CHECKS,
        UserFsm.DOCTOR_TREATS,
    ),
    F.text,
)
async def allies_communicate(
    message: Message,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    user_manager = UserManager(
        message=message, state=state, dispatcher=dispatcher
    )
    await user_manager.allies_communicate()
