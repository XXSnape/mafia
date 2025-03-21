from dataclasses import dataclass

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, PollAnswer
from sqlalchemy.ext.asyncio import AsyncSession

from database.dao.prohibited_roles import ProhibitedRolesDAO
from database.schemas.roles import UserTgId


@dataclass
class RouterHelper:
    callback: CallbackQuery | None = None
    state: FSMContext | None = None
    session: AsyncSession | None = None
    poll_answer: PollAnswer | None = None

    async def _get_banned_roles(self):
        dao = ProhibitedRolesDAO(session=self.session)
        result = await dao.find_all(
            UserTgId(user_tg_id=self.callback.from_user.id)
        )
        return [record.role for record in result]
