from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.inline.callback_factory.settings import (
    GroupSettingsCbData,
)
from middlewares.db import DatabaseMiddlewareWithCommit
from services.common.settings import SettingsRouter


router = Router(name=__name__)


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
