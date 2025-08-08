from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, TelegramObject
from general.exceptions import ActionPerformed
from loguru import logger
from utils.tg import delete_message


class CallbackTimelimiterMiddleware(BaseMiddleware):
    """
    Ограничивает возможность нажать на кнопку спустя некоторое количество минут.
    """

    def __init__(self, minutes: int):
        self.minutes = minutes

    async def __call__(
        self,
        handler: Callable[
            [TelegramObject, dict[str, Any]], Awaitable[Any]
        ],
        callback: CallbackQuery,
        data: dict[str, Any],
    ) -> Any:
        sending_time = callback.message.date
        if sending_time != 0:
            now = datetime.now(UTC)

            minutes = (now - sending_time).seconds // 60
            if minutes > self.minutes - 1:
                await callback.answer(
                    "🙂Кнопка устарела, нажми новую", show_alert=True
                )
                try:
                    await delete_message(
                        message=callback.message,
                        raise_exception=True,
                    )
                except ActionPerformed:
                    await callback.message.delete_reply_markup()
                logger.warning(
                    "Пользователь {} ({}) "
                    "использует устаревшую кнопку ({}) с текстом:\n\n{}\n\n"
                    "Отправленную {}, в {} через {} минут",
                    callback.from_user.full_name,
                    callback.from_user.id,
                    callback.message.message_id,
                    callback.message.text,
                    sending_time,
                    now,
                    minutes,
                )
                return None
        return await handler(callback, data)
