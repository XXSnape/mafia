from dataclasses import dataclass

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, PollAnswer
from sqlalchemy.ext.asyncio import AsyncSession

from database.dao.prohibited_roles import ProhibitedRolesDAO
from database.schemas.roles import UserTgId
from utils.utils import make_build


@dataclass
class RouterHelper:
    callback: CallbackQuery | None = None
    state: FSMContext | None = None
    session: AsyncSession | None = None
    poll_answer: PollAnswer | None = None
    REQUIRE_TO_SAVE: str = make_build(
        "❗️Чтобы сохранить изменения, нажмите «Сохранить💾»\n\n"
    )

    def _get_user_id(self):
        return (
            self.poll_answer.user.id
            if self.poll_answer
            else self.callback.from_user.id
        )

    def _get_bot(self):
        return (
            self.poll_answer.bot
            if self.poll_answer
            else self.callback.bot
        )

    async def _get_banned_roles(self):
        user_id = self._get_user_id()
        dao = ProhibitedRolesDAO(session=self.session)
        result = await dao.find_all(UserTgId(user_tg_id=user_id))
        return [record.role for record in result]
