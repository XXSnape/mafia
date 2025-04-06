from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.state import default_state
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from database.dao.users import UsersDao
from database.schemas.common import TgId
from middlewares.db import DatabaseMiddlewareWithCommit

router = Router(name=__name__)
router.message.filter(F.chat.type == ChatType.PRIVATE)
router.message.middleware(DatabaseMiddlewareWithCommit())


@router.message(CommandStart(), StateFilter(default_state))
async def greetings_to_user(
    message: Message, session_with_commit: AsyncSession
):
    await UsersDao(session=session_with_commit).create_user(
        tg_id=TgId(tg_id=message.from_user.id)
    )
    await message.answer(
        f"Привет, я бот ведущий в для мафии. Просто добавь меня в чат."
    )
