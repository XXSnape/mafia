from aiogram import Dispatcher, F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from services.game.processing_user_actions import UserManager
from states.game import UserFsm

router = Router(name=__name__)


@router.message(
    StateFilter(
        UserFsm.BASIC_ROLE_WITH_ALLIES,
        UserFsm.POLICEMAN,
        UserFsm.FORGER,
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
