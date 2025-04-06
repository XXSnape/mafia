from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.filters import (
    Command,
    StateFilter,
)
from aiogram.fsm.state import default_state
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from database.dao.groups import GroupsDao
from database.schemas.common import TgId
from keyboards.inline.keypads.settings import set_up_group_kb
from middlewares.db import (
    DatabaseMiddlewareWithoutCommit,
)
from services.settings.banned_roles import RoleAttendant
from services.settings.order_of_roles import RoleManager
from utils.pretty_text import make_build
from utils.tg import check_user_for_admin_rights, delete_message

router = Router(name=__name__)
router.message.filter(
    F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP})
)
router.message.middleware(DatabaseMiddlewareWithoutCommit())


@router.message(Command("settings"), StateFilter(default_state))
async def get_group_settings(
    message: Message, session_without_commit: AsyncSession
):
    await delete_message(message)
    groups_dao = GroupsDao(session=session_without_commit)
    group_tg_id = message.chat.id
    group_schema = await groups_dao.get_group_settings(
        group_tg_id=TgId(tg_id=group_tg_id)
    )
    is_user_admin = await check_user_for_admin_rights(
        bot=message.bot,
        chat_id=group_tg_id,
        user_id=message.from_user.id,
    )
    chat_info = await message.bot.get_chat(group_tg_id)
    group_name = f"Группа {chat_info.title}\n\n"
    if group_schema.banned_roles is None:
        await message.bot.send_message(
            chat_id=message.from_user.id,
            text=group_name
            + make_build(
                "В данной группе применяются настройки любого желающего,"
                " если он начнёт регистрацию!"
            ),
        )
    else:
        banned_roles_text = RoleAttendant.get_banned_roles_text(
            roles_ids=group_schema.banned_roles
        )
        order_of_roles_text = RoleManager.get_current_order_text(
            selected_roles=group_schema.order_of_roles, to_save=False
        )
        other_settings_text = make_build(
            f"Другие настройки:\n\n"
            f"Ночь длится (в секундах): {group_schema.time_for_night}\n"
            f"День длится (в секундах): {group_schema.time_for_day}\n"
        )
        await message.bot.send_message(
            chat_id=message.from_user.id,
            text=group_name + banned_roles_text,
        )
        await message.bot.send_message(
            chat_id=message.from_user.id,
            text=group_name + order_of_roles_text,
        )
        await message.bot.send_message(
            chat_id=message.from_user.id,
            text=group_name + other_settings_text,
        )
    if is_user_admin:
        await message.bot.send_message(
            chat_id=message.from_user.id,
            text=group_name
            + make_build(
                "Ты можешь поменять настройки с помощью кнопок ниже:"
            ),
            reply_markup=set_up_group_kb(group_id=group_schema.id),
        )
