from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from keyboards.inline.callback_factory.help import OrderOfRolesCbData
from keyboards.inline.cb.cb_text import (
    CLEAR_ORDER_OF_ROLES_CB,
    DELETE_LATEST_ROLE_IN_ORDER_CB,
    EDIT_ORDER_OF_ROLES_CB,
    SAVE_ORDER_OF_ROLES_CB,
    VIEW_ORDER_OF_ROLES_CB,
)
from services.users.order_of_roles import RoleManager
from sqlalchemy.ext.asyncio import AsyncSession

router = Router(name=__name__)


@router.callback_query(F.data == VIEW_ORDER_OF_ROLES_CB)
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


@router.callback_query(F.data == CLEAR_ORDER_OF_ROLES_CB)
async def clear_order_of_roles(
    callback: CallbackQuery,
    state: FSMContext,
    session_with_commit: AsyncSession,
):
    manager = RoleManager(
        callback=callback, state=state, session=session_with_commit
    )
    await manager.clear_order_of_roles()


@router.callback_query(F.data == EDIT_ORDER_OF_ROLES_CB)
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


@router.callback_query(OrderOfRolesCbData.filter())
async def add_new_role_to_queue(
    callback: CallbackQuery,
    state: FSMContext,
    session_with_commit: AsyncSession,
    callback_data: OrderOfRolesCbData,
):
    manager = RoleManager(
        callback=callback, state=state, session=session_with_commit
    )
    await manager.add_new_role_to_queue(callback_data=callback_data)


@router.callback_query(
    F.data == DELETE_LATEST_ROLE_IN_ORDER_CB,
)
async def pop_latest_role_in_order(
    callback: CallbackQuery,
    state: FSMContext,
):
    manager = RoleManager(callback=callback, state=state)
    await manager.pop_latest_role_in_order()


@router.callback_query(F.data == SAVE_ORDER_OF_ROLES_CB)
async def save_order_of_roles(
    callback: CallbackQuery,
    state: FSMContext,
    session_with_commit: AsyncSession,
):
    manager = RoleManager(
        callback=callback, state=state, session=session_with_commit
    )
    await manager.save_order_of_roles()
