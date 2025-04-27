from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery
from keyboards.inline.cb import cb_text
from keyboards.inline.cb.cb_text import (
    FOG_OF_WAR_CB,
    DIFFERENT_SETTINGS_CB,
)
from services.users.different_settings import DifferentSettings
from sqlalchemy.ext.asyncio import AsyncSession

from states.settings import SettingsFsm

router = Router(name=__name__)


@router.callback_query(F.data == FOG_OF_WAR_CB)
async def show_fog_of_war_options(
    callback: CallbackQuery,
    state: FSMContext,
    session_without_commit: AsyncSession,
):
    fog_of_war = DifferentSettings(
        callback=callback,
        state=state,
        session=session_without_commit,
    )
    await fog_of_war.show_fog_of_war_options()


@router.callback_query(
    F.data.in_(
        (
            cb_text.SHOW_KILLERS_CB,
            cb_text.SHOW_INFORMATION_IN_SHARED_CHAT_CB,
            cb_text.SHOW_INFORMATION_ABOUT_GUESTS_AT_NIGHT_CB,
            cb_text.SHOW_USERNAMES_DURING_VOTING_CB,
        )
    ),
)
async def change_settings_for_non_deceased_roles(
    callback: CallbackQuery,
    state: FSMContext,
    session_with_commit: AsyncSession,
):
    fog_of_war = DifferentSettings(
        callback=callback,
        state=state,
        session=session_with_commit,
    )
    await fog_of_war.change_settings_for_non_deceased_roles()


@router.callback_query(
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
    fog_of_war = DifferentSettings(
        callback=callback,
        state=state,
        session=session_with_commit,
    )
    await fog_of_war.change_settings_related_to_deceased_roles()


@router.callback_query(F.data == DIFFERENT_SETTINGS_CB)
async def show_common_settings_options(
    callback: CallbackQuery,
    state: FSMContext,
    session_without_commit: AsyncSession,
):
    different_settings = DifferentSettings(
        callback=callback,
        state=state,
        session=session_without_commit,
    )
    await different_settings.show_common_settings_options()


@router.callback_query(
    F.data.in_(
        (
            cb_text.CAN_KILL_TEAMMATES_CB,
            cb_text.CAN_MARSHAL_KILL_CB,
            cb_text.MAFIA_EVERY_3_CB,
        )
    )
)
async def change_different_settings(
    callback: CallbackQuery,
    state: FSMContext,
    session_with_commit: AsyncSession,
):
    different_settings = DifferentSettings(
        callback=callback, state=state, session=session_with_commit
    )
    await different_settings.change_different_settings()
