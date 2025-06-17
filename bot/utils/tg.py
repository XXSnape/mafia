import asyncio
from contextlib import suppress
from datetime import timedelta

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError, TelegramRetryAfter
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    ChatMemberAdministrator,
    ChatMemberBanned,
    ChatMemberLeft,
    ChatMemberOwner,
    ChatPermissions,
    InlineKeyboardMarkup,
    Message,
)
from cache.cache_types import PlayersIds
from general.exceptions import ActionPerformed
from loguru import logger


async def delete_message(
    message: Message, raise_exception: bool = False
):
    try:
        await message.delete()
    except (TelegramAPIError, AttributeError):
        if raise_exception:
            raise ActionPerformed


async def delete_message_by_chat(
    bot: Bot, chat_id: int, message_id: int
):
    with suppress(TelegramAPIError):
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


async def checking_for_presence_in_group(
    bot: Bot, chat_id: int, user_id: int
):
    member = await bot.get_chat_member(
        chat_id=chat_id, user_id=user_id
    )
    return (
        isinstance(
            member,
            (
                ChatMemberLeft,
                ChatMemberBanned,
            ),
        )
        is False
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
    with suppress(TelegramAPIError):
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


async def resending_message(
    bot: Bot,
    chat_id: int,
    text: str,
    photo: str | None = None,
    protect_content: bool = False,
    reply_markup: InlineKeyboardMarkup | None = None,
    repeats: int = 2,
) -> Message:

    copy_repeats = repeats
    while copy_repeats > 0:
        copy_repeats -= 1
        if photo:
            coro = bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=text,
                reply_markup=reply_markup,
                protect_content=protect_content,
            )
        else:
            coro = bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=reply_markup,
                protect_content=protect_content,
            )
        try:
            result = await coro
            return result
        except TelegramRetryAfter as e:
            if copy_repeats == 0:
                logger.error(
                    "Не удалось отправить сообщение после {} попыток",
                    repeats,
                )
                raise e
            logger.warning(
                "Не удалось отправить сообщение, блокировка на {} секунд.\n"
                "Осталось попыток: {} из {}",
                e.retry_after,
                copy_repeats,
                repeats,
            )
            await asyncio.sleep(e.retry_after + 1)
        except TelegramAPIError:
            logger.exception("Не удалось отправить сообщение")
            raise
