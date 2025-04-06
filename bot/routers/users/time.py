from aiogram import Router, F

from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.inline.callback_factory.settings import (
    TimeOfDayCbData,
)
from keyboards.inline.cb.cb_text import (
    LENGTH_OF_NIGHT_CB,
    LENGTH_OF_DAY_CB,
)
from services.users.time import TimeRouter

router = Router(name=__name__)


@router.callback_query(
    F.data.in_((LENGTH_OF_NIGHT_CB, LENGTH_OF_DAY_CB))
)
async def edit_game_time(
    callback: CallbackQuery, session_without_commit: AsyncSession
):
    time_router = TimeRouter(
        callback=callback, session=session_without_commit
    )
    await time_router.edit_game_time()


@router.callback_query(TimeOfDayCbData.filter())
async def changes_length_of_time_of_day(
    callback: CallbackQuery,
    callback_data: TimeOfDayCbData,
    session_with_commit: AsyncSession,
):
    time_router = TimeRouter(
        callback=callback, session=session_with_commit
    )
    await time_router.changes_length_of_time_of_day(
        callback_data=callback_data
    )
