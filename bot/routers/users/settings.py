from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from keyboards.inline.callback_factory.settings import (
    GroupSettingsCbData,
)
from keyboards.inline.cb.cb_text import (
    ACTIONS_ON_SETTINGS_CB,
)
from services.common.settings import SettingsRouter

router = Router(name=__name__)


@router.callback_query(
    F.data == ACTIONS_ON_SETTINGS_CB,
)
async def back_to_settings(
    callback: CallbackQuery, state: FSMContext
):
    settings = SettingsRouter(callback=callback, state=state)
    await settings.back_to_settings()


@router.callback_query(GroupSettingsCbData.filter())
async def start_changing_settings(
    callback: CallbackQuery,
    callback_data: GroupSettingsCbData,
    state: FSMContext,
):
    settings = SettingsRouter(callback=callback, state=state)
    await settings.start_changing_settings(
        callback_data=callback_data
    )
