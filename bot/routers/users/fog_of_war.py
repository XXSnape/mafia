from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery
from keyboards.inline.cb import cb_text
from keyboards.inline.cb.cb_text import (
    FOG_OF_WAR_CB,
)
from services.users.fog_of_war import FogOfWar
from sqlalchemy.ext.asyncio import AsyncSession

from states.settings import SettingsFsm

router = Router(name=__name__)


@router.callback_query(default_state, F.data == FOG_OF_WAR_CB)
async def show_fog_of_war_options(
    callback: CallbackQuery,
    state: FSMContext,
    session_without_commit: AsyncSession,
):
    fog_of_war = FogOfWar(
        callback=callback,
        state=state,
        session=session_without_commit,
    )
    await fog_of_war.show_options()


@router.callback_query(
    SettingsFsm.FOG_OF_WAR,
    F.data.in_(
        (
            cb_text.SHOW_KILLERS_CB,
            cb_text.SHOW_INFORMATION_IN_SHARED_CHAT_CB,
            cb_text.SHOW_INFORMATION_ABOUT_GUESTS_AT_NIGHT_CB,
        )
    ),
)
async def change_settings_for_non_deceased_roles(
    callback: CallbackQuery,
    state: FSMContext,
    session_with_commit: AsyncSession,
):
    fog_of_war = FogOfWar(
        callback=callback,
        state=state,
        session=session_with_commit,
    )
    await fog_of_war.change_settings_for_non_deceased_roles()


@router.callback_query(
    SettingsFsm.FOG_OF_WAR,
    F.data.in_(
        (
            cb_text.SHOW_DEAD_ROLES_AFTER_NIGHT_CB,
            cb_text.SHOW_DEAD_ROLES_AFTER_HANGING_CB,
            cb_text.SHOW_ROLES_DIED_DUE_TO_INACTIVITY_CB,
        )
    ),
)
async def change_settings_related_to_deceased_roles(
    callback: CallbackQuery,
    state: FSMContext,
    session_with_commit: AsyncSession,
):
    fog_of_war = FogOfWar(
        callback=callback,
        state=state,
        session=session_with_commit,
    )
    await fog_of_war.change_settings_related_to_deceased_roles()
