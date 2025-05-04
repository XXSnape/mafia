import asyncio
from contextlib import suppress
from datetime import timedelta

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    ChatMemberAdministrator,
    ChatMemberOwner,
    ChatPermissions,
    Message,
)
from cache.cache_types import PlayersIds
from general.exceptions import ActionPerformed


async def delete_message(
    message: Message, raise_exception: bool = False
):
    try:
        await message.delete()
    except (TelegramBadRequest, AttributeError):
        if raise_exception:
            raise ActionPerformed


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
    state: FSMContext,
):
    game_data = await state.get_data()
    to_delete = game_data["to_delete"]
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
    game_data["to_delete"] = []
    await state.set_data(game_data)
    return game_data


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


async def unban_users(bot: Bot, chat_id: int, users: PlayersIds):
    await asyncio.gather(
        *(
            bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                permissions=ChatPermissions(
                    can_send_messages=True,
                    can_send_other_messages=True,
                    can_send_polls=True,
                ),
            )
            for user_id in users
        ),
        return_exceptions=True
    )
