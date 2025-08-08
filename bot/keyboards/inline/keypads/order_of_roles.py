from _operator import attrgetter
from aiogram.types import InlineKeyboardButton
from cache.cache_types import OrderOfRolesCache
from general import settings
from general.collection_of_roles import get_data_with_roles
from general.text import TO_SAVE
from keyboards.inline.builder import generate_inline_kb
from keyboards.inline.buttons.common import (
    BACK_TO_SELECTING_ACTIONS_ON_SETTINGS_BTN,
    CANCEL_BTN,
)
from keyboards.inline.callback_factory.help import OrderOfRolesCbData
from keyboards.inline.cb.cb_text import (
    CLEAR_ORDER_OF_ROLES_CB,
    DELETE_LATEST_ROLE_IN_ORDER_CB,
    EDIT_ORDER_OF_ROLES_CB,
    SAVE_ORDER_OF_ROLES_CB,
)

from mafia.roles import MafiaAlias


def edit_order_of_roles_kb(are_there_roles: bool):
    buttons = [
        InlineKeyboardButton(
            text="Редактировать✏️",
            callback_data=EDIT_ORDER_OF_ROLES_CB,
        )
    ]
    if are_there_roles:
        buttons.append(
            InlineKeyboardButton(
                text="Очистить все🗑️",
                callback_data=CLEAR_ORDER_OF_ROLES_CB,
            )
        )

    buttons.append(BACK_TO_SELECTING_ACTIONS_ON_SETTINGS_BTN)

    return generate_inline_kb(data_with_buttons=buttons)


def get_next_role_kb(
    order_data: OrderOfRolesCache, automatic_attacking: bool = True
):
    all_roles = get_data_with_roles()
    buttons = []
    divider = 3 if order_data["criminal_every_3"] else 4
    if (len(order_data["selected"]) + 1) % divider == 0:
        if automatic_attacking and len(order_data["attacking"]) == 1:
            order_data["selected"].append(MafiaAlias.role_id)
            return get_next_role_kb(order_data)
        key = "attacking"
    else:
        key = "other"
    for role_id in order_data[key]:
        current_role = all_roles[role_id]
        buttons.append(
            InlineKeyboardButton(
                text=current_role.role
                + current_role.grouping.value.name[-1],
                callback_data=OrderOfRolesCbData(
                    role_id=role_id
                ).pack(),
            )
        )
    buttons.sort(key=attrgetter("text"))
    if (
        len(order_data["selected"])
        > settings.mafia.minimum_number_of_players
    ):
        buttons.append(
            InlineKeyboardButton(
                text="🗑️Убрать последний",
                callback_data=DELETE_LATEST_ROLE_IN_ORDER_CB,
            )
        )
    buttons.extend(
        [
            InlineKeyboardButton(
                text=TO_SAVE,
                callback_data=SAVE_ORDER_OF_ROLES_CB,
            ),
            CANCEL_BTN,
        ]
    )
    return generate_inline_kb(
        data_with_buttons=buttons, leave_1_each=3
    )
