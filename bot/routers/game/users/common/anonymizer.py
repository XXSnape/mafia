from aiogram import Dispatcher, Router
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from general.commands import PrivateCommands
from services.game.processing_user_actions import UserManager
from sqlalchemy.ext.asyncio import AsyncSession

router = Router(name=__name__)


@router.message(Command(PrivateCommands.anon.name))
async def send_anonymously_to_group(
    message: Message,
    command: CommandObject,
    session_with_commit: AsyncSession,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    user_manager = UserManager(
        message=message,
        session=session_with_commit,
        state=state,
        dispatcher=dispatcher,
    )
    await user_manager.send_anonymously_to_group(command=command)
