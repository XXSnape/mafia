from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.filters import (
    Command,
    StateFilter,
)
from aiogram.fsm.state import default_state
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from database.dao.groups import GroupsDao
from database.schemas.common import TgId
from keyboards.inline.keypads.settings import set_up_group_kb
from middlewares.db import (
    DatabaseMiddlewareWithoutCommit,
)
from services.common.settings import SettingsRouter
from services.users.banned_roles import RoleAttendant
from services.users.order_of_roles import RoleManager
from utils.pretty_text import make_build
from utils.tg import check_user_for_admin_rights, delete_message

router = Router(name=__name__)


@router.message(Command("settings"), StateFilter(default_state))
async def get_group_settings(
    message: Message, session_without_commit: AsyncSession
):
    settings = SettingsRouter(
        message=message, session=session_without_commit
    )
    await settings.get_group_settings()
