from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from database.dao.groups import GroupsDao
from database.dao.settings import SettingsDao
from database.schemas.common import IdSchema, TgId, UserTgId
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
from states.settings import SettingsFsm
from utils.pretty_text import make_build
from utils.tg import delete_message, check_user_for_admin_rights

router = Router(name=__name__)


@router.callback_query(F.data == MENU_CB)
async def get_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "Доступные команды:\n\n/users - настройки"
    )


@router.callback_query(F.data == CANCEL_CB)
async def cancel_state(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer("/my_settings - настройки")


@router.message(
    Command("my_settings"),
    StateFilter(
        default_state,
        SettingsFsm.BAN_ROLES,
        SettingsFsm.ORDER_OF_ROLES,
    ),
)
async def handle_settings(message: Message, state: FSMContext):
    await state.clear()
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
