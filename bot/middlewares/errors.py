from contextlib import suppress
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.exceptions import TelegramAPIError
from aiogram.types import CallbackQuery, Message, TelegramObject
from general.exceptions import ActionPerformed
from loguru import logger
from utils.pretty_text import make_build
from utils.tg import delete_message


class HandleCallbackErrorMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[
            [TelegramObject, Dict[str, Any]], Awaitable[Any]
        ],
        callback: CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        """
        Обрабатывает любые ошибки при нажатии на кнопку
        :param handler: обработчик
        :param callback: CallbackQuery
        :param data: Dict[str, Any]
        :return: Any
        """
        try:
            return await handler(callback, data)
        except ActionPerformed:
            await callback.answer(
                text="🙂Не спеши! Скоро тебе придет сообщение о подтверждении твоих намерений!"
            )
        except Exception as e:
            await callback.answer(
                "🙂Попробуй еще раз", show_alert=True
            )
            await delete_message(callback.message)
            logger.exception("Произошла ошибка в callback")


class HandleMessageErrorMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[
            [TelegramObject, Dict[str, Any]], Awaitable[Any]
        ],
        message: Message,
        data: Dict[str, Any],
    ) -> Any:
        """
        Обрабатывает любые ошибки при нажатии на кнопку
        :param handler: обработчик
        :param message: Message
        :param data: Dict[str, Any]
        :return: Any
        """
        try:
            return await handler(message, data)
        except Exception:
            with suppress(TelegramAPIError):
                await message.answer(
                    make_build("Попробуй еще раз...")
                )
            logger.exception("Произошла ошибка в message")


class HandleDeletionOrEditionErrorMiddleware(BaseMiddleware):
    """Если происходит ошибка от телеграма,
    пользователю показывается окно с сообщением error_message"""

    def __init__(self, error_message: str):
        self.error_message = error_message

    async def __call__(
        self,
        handler: Callable[
            [TelegramObject, Dict[str, Any]], Awaitable[Any]
        ],
        callback: CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        try:
            return await handler(callback, data)
        except TelegramAPIError:
            await callback.answer(
                text=f"🙂{self.error_message}", show_alert=True
            )
            try:
                await delete_message(
                    message=callback.message, raise_exception=True
                )
            except ActionPerformed:
                await callback.message.delete_reply_markup()
            return None
