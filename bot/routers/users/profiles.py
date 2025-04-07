from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from services.common.statistics import StatisticsRouter

router = Router(name=__name__)


@router.message(Command("profile"))
async def get_my_profile(
    message: Message, session_without_commit: AsyncSession
):
    statistics = StatisticsRouter(
        message=message, session=session_without_commit
    )
    await statistics.get_my_profile()
