from aiogram import F, Router
from aiogram.filters import and_f, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery
from general.collection_of_roles import get_data_with_roles
from keyboards.inline.cb.cb_text import (
    BAN_EVERYTHING_CB,
    CANCEL_CB,
    CLEAR_SETTINGS_CB,
    EDIT_SETTINGS_CB,
    SAVE_CB,
    VIEW_BANNED_ROLES_CB,
)
from services.users.banned_roles import RoleAttendant
from sqlalchemy.ext.asyncio import AsyncSession
from states.settings import SettingsFsm

router = Router(name=__name__)


@router.callback_query(
    or_f(
        and_f(default_state, F.data == VIEW_BANNED_ROLES_CB),
        and_f(SettingsFsm.BAN_ROLES, F.data == CANCEL_CB),
    )
)
async def view_banned_roles(
    callback: CallbackQuery,
    state: FSMContext,
    session_without_commit: AsyncSession,
):
    attendant = RoleAttendant(
        callback=callback,
        state=state,
        session=session_without_commit,
    )
    await attendant.view_banned_roles()


@router.callback_query(
    SettingsFsm.BAN_ROLES, F.data == CLEAR_SETTINGS_CB
)
async def clear_banned_roles(
    callback: CallbackQuery,
    state: FSMContext,
    session_with_commit: AsyncSession,
):
    attendant = RoleAttendant(
        callback=callback, state=state, session=session_with_commit
    )
    await attendant.clear_banned_roles()


@router.callback_query(
    SettingsFsm.BAN_ROLES, F.data == BAN_EVERYTHING_CB
)
async def ban_everything(
    callback: CallbackQuery,
    state: FSMContext,
    session_with_commit: AsyncSession,
):
    attendant = RoleAttendant(
        callback=callback, state=state, session=session_with_commit
    )
    await attendant.ban_everything()


@router.callback_query(
    SettingsFsm.BAN_ROLES, F.data == EDIT_SETTINGS_CB
)
async def suggest_roles_to_ban(
    callback: CallbackQuery,
    state: FSMContext,
):
    attendant = RoleAttendant(callback=callback, state=state)
    await attendant.suggest_roles_to_ban()


@router.callback_query(
    SettingsFsm.BAN_ROLES, F.data.in_(get_data_with_roles().keys())
)
async def process_banned_roles(
    callback: CallbackQuery,
    state: FSMContext,
):
    attendant = RoleAttendant(
        callback=callback,
        state=state,
    )
    await attendant.process_banned_roles()


@router.callback_query(SettingsFsm.BAN_ROLES, F.data == SAVE_CB)
async def save_prohibited_roles(
    callback: CallbackQuery,
    state: FSMContext,
    session_with_commit: AsyncSession,
):
    attendant = RoleAttendant(
        callback=callback, state=state, session=session_with_commit
    )
    await attendant.save_prohibited_roles()
