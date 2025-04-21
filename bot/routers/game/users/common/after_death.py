from aiogram import Dispatcher, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from services.game.processing_user_actions import UserManager
from states.game import UserFsm

router = Router(name=__name__)


@router.message(F.text, UserFsm.WAIT_FOR_LATEST_LETTER)
async def send_latest_message(
    message: Message,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    user_manager = UserManager(
        message=message, state=state, dispatcher=dispatcher
    )
    await user_manager.send_latest_message()
