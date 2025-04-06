from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.filters import or_f, and_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from general.collection_of_roles import get_data_with_roles
from keyboards.inline.cb.cb_text import (
    VIEW_ORDER_OF_ROLES_CB,
    EDIT_SETTINGS_CB,
    SAVE_CB,
    CLEAR_SETTINGS_CB,
    CANCEL_CB,
    DELETE_LATEST_ROLE_IN_ORDER_CB,
)
from middlewares.db import (
    DatabaseMiddlewareWithCommit,
    DatabaseMiddlewareWithoutCommit,
)

from services.users.order_of_roles import RoleManager
from states.settings import SettingsFsm

router = Router(name=__name__)


@router.callback_query(
    or_f(
        F.data == VIEW_ORDER_OF_ROLES_CB,
        and_f(SettingsFsm.ORDER_OF_ROLES, F.data == CANCEL_CB),
    )
)
async def view_order_of_roles(
    callback: CallbackQuery,
    state: FSMContext,
    session_without_commit: AsyncSession,
):
    manager = RoleManager(
        callback=callback,
        state=state,
        session=session_without_commit,
    )
    await manager.view_order_of_roles()


@router.callback_query(
    SettingsFsm.ORDER_OF_ROLES, F.data == CLEAR_SETTINGS_CB
)
async def clear_order_of_roles(
    callback: CallbackQuery,
    state: FSMContext,
    session_with_commit: AsyncSession,
):
    manager = RoleManager(
        callback=callback, state=state, session=session_with_commit
    )
    await manager.clear_order_of_roles()


@router.callback_query(
    SettingsFsm.ORDER_OF_ROLES, F.data == EDIT_SETTINGS_CB
)
async def start_editing_order(
    callback: CallbackQuery,
    state: FSMContext,
    session_without_commit: AsyncSession,
):
    manager = RoleManager(
        callback=callback,
        state=state,
        session=session_without_commit,
    )
    await manager.start_editing_order()


@router.callback_query(
    SettingsFsm.ORDER_OF_ROLES,
    F.data.in_(get_data_with_roles().keys()),
)
async def add_new_role_to_queue(
    callback: CallbackQuery,
    state: FSMContext,
    session_with_commit: AsyncSession,
):
    manager = RoleManager(
        callback=callback, state=state, session=session_with_commit
    )
    await manager.add_new_role_to_queue()


@router.callback_query(
    SettingsFsm.ORDER_OF_ROLES,
    F.data == DELETE_LATEST_ROLE_IN_ORDER_CB,
)
async def pop_latest_role_in_order(
    callback: CallbackQuery,
    state: FSMContext,
):
    manager = RoleManager(callback=callback, state=state)
    await manager.pop_latest_role_in_order()


@router.callback_query(SettingsFsm.ORDER_OF_ROLES, F.data == SAVE_CB)
async def save_order_of_roles(
    callback: CallbackQuery,
    state: FSMContext,
    session_with_commit: AsyncSession,
):
    manager = RoleManager(
        callback=callback, state=state, session=session_with_commit
    )
    await manager.save_order_of_roles()
