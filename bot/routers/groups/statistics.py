from aiogram import Router
from aiogram.filters import (
    Command,
)
from aiogram.types import Message
from services.common.statistics import StatisticsRouter
from sqlalchemy.ext.asyncio import AsyncSession

router = Router(name=__name__)


@router.message(Command("statistics"))
async def get_group_statistics(
    message: Message, session_without_commit: AsyncSession
):
    statistics = StatisticsRouter(
        message=message, session=session_without_commit
    )
    await statistics.get_group_statistics()
