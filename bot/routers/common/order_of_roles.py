from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from cache.cache_types import OrderOfRolesCache
from database.dao.order import OrderOfRolesDAO
from database.dao.prohibited_roles import (
    ProhibitedRolesDAO,
)
from database.schemas.roles import UserTgId
from general.collection_of_roles import get_data_with_roles
from keyboards.inline.cb.cb_text import (
    VIEW_ORDER_OF_ROLES_CB,
    EDIT_SETTINGS_CB,
    SAVE_CB,
)
from keyboards.inline.keypads.settings import (
    get_next_role_kb,
    edit_roles_kb,
)
from middlewares.db import (
    DatabaseMiddlewareWithCommit,
    DatabaseMiddlewareWithoutCommit,
)
from services.roles.base.roles import Groupings
from services import roles
from states.settings import SettingsFsm

router = Router(name=__name__)
router.message.filter(F.chat.type == ChatType.PRIVATE)
router.callback_query.filter(F.message.chat.type == ChatType.PRIVATE)
router.message.middleware(DatabaseMiddlewareWithCommit())
router.callback_query.middleware(DatabaseMiddlewareWithCommit())
router.callback_query.middleware(DatabaseMiddlewareWithoutCommit())


def get_current_order(selected_roles: list[str]):
    all_roles = get_data_with_roles()
    result = "Текущий порядок ролей:\n\n"
    for index, role in enumerate(selected_roles, 1):
        result += f"{index}) {all_roles[role].role}\n"
    return result


@router.callback_query(F.data == VIEW_ORDER_OF_ROLES_CB)
async def view_order_of_roles(
    callback: CallbackQuery,
    state: FSMContext,
    session_without_commit: AsyncSession,
):
    dao = OrderOfRolesDAO(session=session_without_commit)
    order_of_roles = await dao.find_all(
        UserTgId(user_tg_id=callback.from_user.id),
        sort_fields=["number"],
    )
    text = "Текущий порядок ролей:\n\n"
    if not order_of_roles:
        bases = [
            roles.Mafia(),
            roles.Doctor(),
            roles.Policeman(),
            roles.Civilian(),
        ]
        for num, role in enumerate(bases, 1):
            text += f"{num}) {role.role}\n"
    else:
        for record in order_of_roles:
            text += f"{record.number}) {record.role}\n"
    await state.set_state(SettingsFsm.ORDER_OF_ROLES)
    await callback.message.edit_text(
        text=text, reply_markup=edit_roles_kb(bool(order_of_roles))
    )


@router.callback_query(
    SettingsFsm.ORDER_OF_ROLES, F.data == EDIT_SETTINGS_CB
)
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


@router.callback_query(
    SettingsFsm.ORDER_OF_ROLES,
    F.data.in_(get_data_with_roles().keys()),
)
async def add_new_role_to_queue(
    callback: CallbackQuery,
    state: FSMContext,
    session_with_commit: AsyncSession,
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
    if len(order_data["selected"]) == 30:
        await callback.answer(
            "Пока можно выбрать только 30 ролей!", show_alert=True
        )
        dao = OrderOfRolesDAO(session=session_with_commit)
        await dao.save_order_of_roles(
            user_id=callback.from_user.id,
            roles=order_data["selected"],
        )
        await callback.message.edit_text(
            text=get_current_order(order_data["selected"])
        ),
        await state.clear()
        return
    markup = get_next_role_kb(order_data=order_data)
    await state.set_data(order_data)
    await callback.message.edit_text(
        text=get_current_order(order_data["selected"]),
        reply_markup=markup,
    )


@router.callback_query(SettingsFsm.ORDER_OF_ROLES, F.data == SAVE_CB)
async def save_order_of_roles(
    callback: CallbackQuery,
    state: FSMContext,
    session_with_commit: AsyncSession,
):
    order_data: OrderOfRolesCache = await state.get_data()
    selected = order_data["selected"]
    text = get_current_order(selected)
    dao = OrderOfRolesDAO(session=session_with_commit)
    await dao.save_order_of_roles(
        user_id=callback.from_user.id,
        roles=order_data["selected"],
    )
    await state.clear()
    await callback.answer(
        "Порядок ролей успешно сохранён!", show_alert=True
    )
    await callback.message.edit_text(text=text)
    await callback.message.answer("/settings - настройки")
