from aiogram import Router
from aiogram.filters import (
    Command,
)
from aiogram.types import Message
from services.common.subscriptions import SubscriptionsRouter
from sqlalchemy.ext.asyncio import AsyncSession

router = Router(name=__name__)


@router.message(Command("subscribe"))
async def subscribe_or_unsubscribe_from_group(
    message: Message, session_with_commit: AsyncSession
):
    subscriptions_router = SubscriptionsRouter(
        message=message, session=session_with_commit
    )
    await subscriptions_router.subscribe_or_unsubscribe_from_group()
