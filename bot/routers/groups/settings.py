from aiogram import Router
from aiogram.filters import (
    Command,
    StateFilter,
)
from aiogram.fsm.state import default_state
from aiogram.types import Message
from general.commands import GroupCommands
from services.common.settings import SettingsRouter
from sqlalchemy.ext.asyncio import AsyncSession

router = Router(name=__name__)


@router.message(
    Command(GroupCommands.settings.name), StateFilter(default_state)
)
async def get_group_settings(
    message: Message, session_with_commit: AsyncSession
):
    settings = SettingsRouter(
        message=message, session=session_with_commit
    )
    await settings.get_group_settings()
