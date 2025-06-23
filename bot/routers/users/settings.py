from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from cache.cache_types import PersonalSettingsCache, AllSettingsCache
from database.dao.users import UsersDao
from database.schemas.common import TgIdSchema
from general.commands import PrivateCommands
from keyboards.inline.callback_factory.settings import (
    GroupSettingsCbData,
)
from keyboards.inline.cb.cb_text import (
    ACTIONS_ON_SETTINGS_CB,
)
from keyboards.inline.keypads.settings import select_setting_kb
from services.base import RouterHelper
from services.common.settings import SettingsRouter
from sqlalchemy.ext.asyncio import AsyncSession
from utils.pretty_text import make_build

router = Router(name=__name__)

SETTINGS = make_build("⚙️Выбери, что конкретно хочешь настроить")


@router.callback_query(
    F.data == ACTIONS_ON_SETTINGS_CB,
)
async def back_to_settings(
    callback: CallbackQuery, state: FSMContext
):
    router_helper = RouterHelper(callback=callback, state=state)
    await router_helper.clear_settings_data()
    await callback.message.edit_text(
        text=SETTINGS,
        reply_markup=select_setting_kb(),
    )


@router.callback_query(GroupSettingsCbData.filter())
async def start_changing_settings(
    callback: CallbackQuery,
    callback_data: GroupSettingsCbData,
    state: FSMContext,
):
    data: PersonalSettingsCache = await state.get_data()
    data["settings"] = AllSettingsCache(
        group_id=callback_data.group_id
    )
    await state.set_data(data)
    await callback.message.edit_text(
        text=SETTINGS,
        reply_markup=select_setting_kb(),
    )
