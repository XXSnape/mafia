from aiogram import Router, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from general.commands import PrivateCommands
from services.game.processing_user_actions import UserManager

router = Router(name=__name__)


@router.message(Command(PrivateCommands.leave.name))
async def want_to_exit_game(
    message: Message,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    user_manager = UserManager(
        message=message,
        state=state,
        dispatcher=dispatcher,
    )
    await user_manager.want_to_leave_game()
