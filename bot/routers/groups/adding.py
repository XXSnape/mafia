from aiogram import Bot, F, Router
from aiogram.enums import ChatType
from aiogram.filters import (
    JOIN_TRANSITION,
    ChatMemberUpdatedFilter,
    CommandStart,
)
from aiogram.types import ChatMemberUpdated, Message
from services.groups.adding import AddingRouter
from sqlalchemy.ext.asyncio import AsyncSession
from utils.tg import delete_message

router = Router(name=__name__)


@router.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION),
    F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}),
)
async def adding_to_group(
    event: ChatMemberUpdated,
    bot: Bot,
    session_with_commit: AsyncSession,
):
    adding = AddingRouter(session=session_with_commit)
    await adding.adding_to_group(event=event, bot=bot)


@router.message(CommandStart())
async def delete_start(message: Message):
    await delete_message(message)


@router.message(F.migrate_to_chat_id)
async def group_to_supergroup_migration(
    message: Message,
    session_with_commit: AsyncSession,
):
    adding = AddingRouter(
        message=message, session=session_with_commit
    )
    await adding.group_to_supergroup_migration()
