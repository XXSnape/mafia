from aiogram import F, Router
from aiogram.types import CallbackQuery
from keyboards.inline.callback_factory.settings import (
    TimeOfDayCbData,
)
from keyboards.inline.cb.cb_text import (
    DURATION_OF_STAGES_CB,
    TIME_FOR_CONFIRMATION_CB,
    TIME_FOR_DAY_CB,
    TIME_FOR_NIGHT_CB,
    TIME_FOR_VOTING_CB,
)
from services.users.time import TimeRouter
from sqlalchemy.ext.asyncio import AsyncSession

router = Router(name=__name__)


@router.callback_query(F.data == DURATION_OF_STAGES_CB)
async def select_stage_of_game(callback: CallbackQuery):
    time_router = TimeRouter(callback=callback)
    await time_router.select_stage_of_game()


@router.callback_query(
    F.data.in_(
        (
            TIME_FOR_NIGHT_CB,
            TIME_FOR_DAY_CB,
            TIME_FOR_VOTING_CB,
            TIME_FOR_CONFIRMATION_CB,
        )
    )
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
