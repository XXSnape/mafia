import asyncio
from contextlib import suppress
from datetime import timedelta

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    ChatMemberOwner,
    ChatMemberAdministrator,
    ChatPermissions,
)


async def delete_message(message: Message):
    with suppress(TelegramBadRequest, AttributeError):
        await message.delete()


async def delete_message_by_chat(
    bot: Bot, chat_id: int, message_id: int
):
    with suppress(TelegramBadRequest):
        await bot.delete_message(
            chat_id=chat_id, message_id=message_id
        )


async def check_user_for_admin_rights(
    bot: Bot, chat_id: int, user_id: int
) -> bool:
    member = await bot.get_chat_member(
        chat_id=chat_id, user_id=user_id
    )
    return isinstance(
        member, (ChatMemberOwner, ChatMemberAdministrator)
    )


async def delete_messages_from_to_delete(
    bot: Bot,
    state: FSMContext | None,
):
    to_delete = (await state.get_data())["to_delete"]
    await asyncio.gather(
        *(
            delete_message_by_chat(
                bot=bot,
                chat_id=chat_id,
                message_id=message_id,
            )
            for chat_id, message_id in to_delete
        )
    )
    await state.update_data({"to_delete": []})


async def ban_user(
    bot: Bot,
    chat_id: int,
    user_id: int,
    until_date: timedelta | None = None,
):
    with suppress(TelegramBadRequest):
        await bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            permissions=ChatPermissions(can_send_messages=False),
            until_date=until_date,
        )
