from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from middlewares.db import DatabaseMiddlewareWithCommit
from services.common.statistics import StatisticsRouter
from sqlalchemy.ext.asyncio import AsyncSession

router = Router(name=__name__)
router.message.middleware(DatabaseMiddlewareWithCommit())


@router.message(Command("profile"))
async def get_my_profile(
    message: Message, session_with_commit: AsyncSession
):
    statistics = StatisticsRouter(
        message=message, session=session_with_commit
    )
    await statistics.get_my_profile()
