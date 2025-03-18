from contextlib import suppress

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message


async def delete_message(message: Message):
    with suppress(TelegramBadRequest, AttributeError):
        await message.delete()
