from aiogram import Router, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from middlewares.db import DatabaseMiddlewareWithCommit
from services.game.registartion import Registration

router = Router(name=__name__)
router.message.middleware(DatabaseMiddlewareWithCommit())


@router.message(CommandStart(deep_link=True))
async def join_to_game(
    message: Message,
    command: CommandObject,
    state: FSMContext,
    dispatcher: Dispatcher,
    session_with_commit: AsyncSession,
):
    registration = Registration(
        message=message,
        state=state,
        dispatcher=dispatcher,
        session=session_with_commit,
    )
    await registration.join_to_game(command=command)
