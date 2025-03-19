from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from cache.cache_types import OrderOfRolesCache
from database.dao.repositories.prohibited_roles import (
    ProhibitedRolesDAO,
)
from general.collection_of_roles import get_data_with_roles
from keyboards.inline.cb.cb_text import EDIT_ORDER_OF_ROLES_CB
from keyboards.inline.keypads.settings import get_next_role_kb
from middlewares.db import (
    DatabaseMiddlewareWithCommit,
    DatabaseMiddlewareWithoutCommit,
)
from services.roles.base.roles import Groupings
from states.settings import SettingsFsm

router = Router(name=__name__)
router.message.filter(F.chat.type == ChatType.PRIVATE)
router.callback_query.filter(F.message.chat.type == ChatType.PRIVATE)
router.message.middleware(DatabaseMiddlewareWithCommit())
router.callback_query.middleware(DatabaseMiddlewareWithCommit())
router.callback_query.middleware(DatabaseMiddlewareWithoutCommit())


def get_current_order(selected_roles: list[str]):
    all_roles = get_data_with_roles()
    result = "Выбери следующую роль. Текущие роли:\n\n"
    for index, role in enumerate(selected_roles, 1):
        result += f"{index}) {all_roles[role].role}\n"
    return result


@router.callback_query(F.data == EDIT_ORDER_OF_ROLES_CB)
async def start_editing_order(
    callback: CallbackQuery,
    state: FSMContext,
    session_without_commit: AsyncSession,
):
    attacking = []
    other = []
    dao = ProhibitedRolesDAO(session=session_without_commit)
    banned_roles = await dao.get_banned_roles(
        user_id=callback.from_user.id
    )
    all_roles = get_data_with_roles()
    for key, role in all_roles.items():
        if role.role not in banned_roles and key not in [
            "don",
            "doctor",
            "policeman",
        ]:
            if role.grouping != Groupings.criminals:
                other.append(key)
            else:
                attacking.append(key)
    selected = [
        "don",
        "doctor",
        "policeman",
        "civilian",
    ]
    order_data: OrderOfRolesCache = {
        "attacking": attacking,
        "other": other,
        "selected": selected,
    }
    await state.set_state(SettingsFsm.ORDER_OF_ROLES)
    await state.set_data(order_data)
    markup = get_next_role_kb(order_data=order_data)
    await callback.message.edit_text(
        text=get_current_order(selected), reply_markup=markup
    )


@router.callback_query(F.data.in_(get_data_with_roles().keys()))
async def add_new_role_to_queue(
    callback: CallbackQuery, state: FSMContext
):
    order_data: OrderOfRolesCache = await state.get_data()
    role = get_data_with_roles(callback.data)
    key = (
        "attacking"
        if role.grouping == Groupings.criminals
        else "other"
    )
    if role.there_may_be_several is False:
        order_data[key].remove(callback.data)
    order_data["selected"].append(callback.data)
    markup = get_next_role_kb(order_data=order_data)
    await state.set_data(order_data)
    await callback.message.edit_text(
        text=get_current_order(order_data["selected"]),
        reply_markup=markup,
    )
