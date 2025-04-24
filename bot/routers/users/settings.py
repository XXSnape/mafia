from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message
from database.dao.users import UsersDao
from database.schemas.common import TgIdSchema
from keyboards.inline.callback_factory.settings import (
    GroupSettingsCbData,
)
from keyboards.inline.cb.cb_text import (
    ACTIONS_FOR_ROLES_CB,
)
from keyboards.inline.keypads.settings import select_setting_kb
from services.common.settings import SettingsRouter
from sqlalchemy.ext.asyncio import AsyncSession
from states.settings import SettingsFsm
from utils.pretty_text import make_build

router = Router(name=__name__)


@router.message(
    Command("my_settings"),
    StateFilter(
        default_state,
        SettingsFsm.BAN_ROLES,
        SettingsFsm.ORDER_OF_ROLES,
    ),
)
async def handle_settings(
    message: Message,
    state: FSMContext,
    session_with_commit: AsyncSession,
):
    await state.clear()
    await message.delete()
    await UsersDao(session=session_with_commit).get_user_or_create(
        tg_id=TgIdSchema(tg_id=message.from_user.id)
    )
    await message.answer(
        make_build("⚙️Выбери, что конкретно хочешь настроить"),
        reply_markup=select_setting_kb(),
    )


@router.callback_query(
    StateFilter(
        default_state,
        SettingsFsm.BAN_ROLES,
        SettingsFsm.ORDER_OF_ROLES,
    ),
    F.data == ACTIONS_FOR_ROLES_CB,
)
async def back_to_settings(
    callback: CallbackQuery, state: FSMContext
):
    await state.clear()
    await callback.message.edit_text(
        text=make_build("⚙️Выбери, что конкретно хочешь настроить"),
        reply_markup=select_setting_kb(),
    )


@router.callback_query(
    GroupSettingsCbData.filter(F.apply_own.is_(False))
)
async def apply_any_settings(
    callback: CallbackQuery,
    callback_data: GroupSettingsCbData,
    session_with_commit: AsyncSession,
):
    settings = SettingsRouter(
        callback=callback, session=session_with_commit
    )
    await settings.apply_any_settings(callback_data=callback_data)


@router.callback_query(
    GroupSettingsCbData.filter(F.apply_own.is_(True))
)
async def apply_my_settings(
    callback: CallbackQuery,
    callback_data: GroupSettingsCbData,
    session_with_commit: AsyncSession,
):
    settings = SettingsRouter(
        callback=callback, session=session_with_commit
    )
    await settings.apply_my_settings(callback_data=callback_data)
