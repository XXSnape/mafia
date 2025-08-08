from typing import TYPE_CHECKING, Optional

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from general import settings
from general.commands import PrivateCommands
from services.users.ai import AIManager

if TYPE_CHECKING:
    from ai.client import RAGSystem


router = Router(name=__name__)


@router.message(Command(PrivateCommands.q.name))
async def answer_question(
    message: Message,
    command: CommandObject,
    ai: Optional["RAGSystem"],
):
    if ai is None:
        await message.answer(settings.ai.unavailable_message)
        return
    ai_manager = AIManager(
        message=message,
    )
    await ai_manager.answer_question(ai=ai, command=command)
