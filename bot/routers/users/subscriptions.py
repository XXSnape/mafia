from aiogram import Router
from aiogram.types import CallbackQuery
from keyboards.inline.callback_factory.subscriptions import (
    GameNotificationCbData,
)
from services.common.subscriptions import SubscriptionsRouter
from sqlalchemy.ext.asyncio import AsyncSession

router = Router(name=__name__)


@router.callback_query(GameNotificationCbData.filter())
async def disable_notifications(
    callback: CallbackQuery,
    callback_data: GameNotificationCbData,
    session_with_commit: AsyncSession,
):
    subscriptions_router = SubscriptionsRouter(
        callback=callback, session=session_with_commit
    )
    await subscriptions_router.disable_notifications(
        callback_data=callback_data
    )
