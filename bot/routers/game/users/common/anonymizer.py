import asyncio

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from html import escape

from sqlalchemy.ext.asyncio import AsyncSession

from middlewares.db import DatabaseMiddlewareWithCommit
from services.game.processing_user_actions import UserManager

router = Router(name=__name__)
router.message.middleware(DatabaseMiddlewareWithCommit())


@router.message(Command("anon"))
async def send_anonymously_to_group(
    message: Message,
    command: CommandObject,
    session_with_commit: AsyncSession,
):
    user_manager = UserManager(
        message=message, session=session_with_commit
    )
    await user_manager.send_anonymously_to_group(command=command)
