from dataclasses import dataclass

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, PollAnswer
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class RouterHelper:
    callback: CallbackQuery | None = None
    state: FSMContext | None = None
    session: AsyncSession | None = None
    poll_answer: PollAnswer | None = None
