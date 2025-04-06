from aiogram import Router, Bot, F
from aiogram.filters import ChatMemberUpdatedFilter, JOIN_TRANSITION
from aiogram.types import ChatMemberUpdated, Message
from sqlalchemy.ext.asyncio import AsyncSession

from database.dao.groups import GroupsDao
from database.schemas.common import TgId
from middlewares.db import DatabaseMiddlewareWithCommit

router = Router(name=__name__)
router.my_chat_member.middleware(DatabaseMiddlewareWithCommit())
router.message.middleware(DatabaseMiddlewareWithCommit())


@router.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION)
)
async def adding_to_group(
    event: ChatMemberUpdated,
    bot: Bot,
    session_with_commit: AsyncSession,
):
    chat_info = await bot.get_chat(event.chat.id)
    group_dao = GroupsDao(session=session_with_commit)
    await group_dao.add(values=TgId(tg_id=event.chat.id))
    if chat_info.permissions.can_send_messages:
        await event.answer(text=f"Привет! Я Мафия!")


@router.message(F.migrate_to_chat_id)
async def group_to_supergroup_migration(
    message: Message,
    session_with_commit: AsyncSession,
):
    group_dao = GroupsDao(session=session_with_commit)
    await group_dao.update(
        filters=TgId(tg_id=message.chat.id),
        values=TgId(tg_id=message.migrate_to_chat_id),
    )
