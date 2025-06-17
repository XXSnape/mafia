from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, TelegramObject
from loguru import logger
from utils.tg import delete_message


class CallbackTimelimiterMiddleware(BaseMiddleware):
    """
    Ограничивает возможность нажать на кнопку спустя 5 минут.
    В норме кнопки во время игры удаляются, но если этого не произошло,
    должно срабатывать это промежуточное ПО и не давать пользователю возможность
    нажать на устаревшие кнопки.
    """

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
            if minutes > 5:
                await callback.answer(
                    "🙂Кнопка устарела, нажми новую", show_alert=True
                )
                await delete_message(message=callback.message)
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
