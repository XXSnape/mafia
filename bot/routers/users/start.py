from aiogram import Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.state import default_state
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from database.dao.users import UsersDao
from database.schemas.common import TgId

router = Router(name=__name__)


@router.message(CommandStart(), StateFilter(default_state))
async def greetings_to_user(
    message: Message, session_with_commit: AsyncSession
):
    await UsersDao(session=session_with_commit).get_user_or_create(
        tg_id=TgId(tg_id=message.from_user.id)
    )
    await message.answer(
        f"Привет, я бот ведущий в для мафии. Просто добавь меня в чат."
    )
