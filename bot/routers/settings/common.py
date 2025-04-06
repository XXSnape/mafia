from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from database.dao.groups import GroupsDao
from database.schemas.common import IdSchema
from database.schemas.groups import GroupSettingIdSchema
from keyboards.inline.callback_factory.settings import (
    GroupSettingsCbData,
)
from keyboards.inline.cb.cb_text import (
    CANCEL_CB,
    MENU_CB,
    ACTIONS_FOR_ROLES_CB,
)
from keyboards.inline.keypads.settings import select_setting_kb
from middlewares.db import DatabaseMiddlewareWithCommit
from utils.pretty_text import make_build
from utils.tg import delete_message, check_user_for_admin_rights

router = Router(name=__name__)
router.message.filter(F.chat.type == ChatType.PRIVATE)
router.callback_query.filter(F.message.chat.type == ChatType.PRIVATE)
router.callback_query.middleware(DatabaseMiddlewareWithCommit())


@router.callback_query(
    GroupSettingsCbData.filter(F.apply_own.is_(False))
)
async def apply_any_settings(
    callback: CallbackQuery,
    callback_data: GroupSettingsCbData,
    session_with_commit: AsyncSession,
):
    groups_dao = GroupsDao(session=session_with_commit)
    group = await groups_dao.find_one_or_none(
        IdSchema(id=callback_data.group_id)
    )
    group_tg_id = group.tg_id
    group_info = await callback.bot.get_chat(group_tg_id)
    is_user_admin = await check_user_for_admin_rights(
        bot=callback.bot,
        chat_id=group_tg_id,
        user_id=callback.from_user.id,
    )
    if is_user_admin is False:
        await callback.answer(
            "🚫Ты больше не админ в этой группе", show_alert=True
        )
        await delete_message(callback.message)
        return
    await groups_dao.update(
        filters=IdSchema(id=callback_data.group_id),
        values=GroupSettingIdSchema(setting_id=None),
    )
    await callback.answer(
        f"✅Теперь в группе {group_info.title} "
        f"разрешены настройки всех желающих, если они начнут регистрацию!",
        show_alert=True,
    )
    await delete_message(callback.message)


@router.callback_query(F.data == MENU_CB)
async def get_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "Доступные команды:\n\n/settings - настройки"
    )


@router.callback_query(F.data == CANCEL_CB)
async def cancel_state(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer("/settings - настройки")


@router.message(Command("settings"), StateFilter(default_state))
async def handle_settings(
    message: Message,
):
    await message.delete()
    await message.answer(
        "Выбери, что конкретно хочешь настроить",
        reply_markup=select_setting_kb(),
    )


@router.callback_query(F.data == ACTIONS_FOR_ROLES_CB)
async def back_to_settings(
    callback: CallbackQuery, state: FSMContext
):
    await state.clear()
    await callback.message.edit_text(
        text="Выбери, что конкретно хочешь настроить",
        reply_markup=select_setting_kb(),
    )
