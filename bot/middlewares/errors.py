from contextlib import suppress
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message, TelegramObject
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
        except Exception as e:
            await callback.answer(
                "Попробуй еще раз...", show_alert=True
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
        except Exception as e:
            with suppress(TelegramBadRequest):
                await message.answer(
                    make_build("Попробуй еще раз...")
                )
            logger.exception("Произошла ошибка в message")
