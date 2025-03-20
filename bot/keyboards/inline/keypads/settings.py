from aiogram.types import InlineKeyboardButton

from cache.cache_types import OrderOfRolesCache
from general.collection_of_roles import get_data_with_roles
from keyboards.inline.builder import generate_inline_kb
from keyboards.inline.cb.cb_text import (
    VIEW_BANNED_ROLES_CB,
    SAVE_CB,
    CANCEL_CB,
    EDIT_SETTINGS_CB,
    CLEAR_SETTINGS_CB,
    VIEW_ORDER_OF_ROLES_CB,
)


def select_setting_kb():
    buttons = [
        InlineKeyboardButton(
            text="Порядок ролей",
            callback_data=VIEW_ORDER_OF_ROLES_CB,
        ),
        InlineKeyboardButton(
            text="Забаненные роли🚫",
            callback_data=VIEW_BANNED_ROLES_CB,
        ),
    ]
    return generate_inline_kb(data_with_buttons=buttons)


def edit_roles_kb(are_there_roles: bool):
    buttons = [
        InlineKeyboardButton(
            text="Редактировать", callback_data=EDIT_SETTINGS_CB
        )
    ]
    if are_there_roles:
        buttons.append(
            InlineKeyboardButton(
                text="Очистить все",
                callback_data=CLEAR_SETTINGS_CB,
            )
        )

    buttons.append(CANCEL_BTN)

    return generate_inline_kb(data_with_buttons=buttons)


def go_to_following_roles_kb(
    current_number: int, max_number: int, are_there_roles: bool
):
    buttons = []
    if current_number != 0:
        buttons.append(
            InlineKeyboardButton(
                text="⏪",
                callback_data=str(current_number - 1),
            )
        )
    if current_number != max_number:
        buttons.append(
            InlineKeyboardButton(
                text="⏩",
                callback_data=str(current_number + 1),
            )
        )
    if are_there_roles:
        buttons.append(SAVE_BTN)
    buttons.append(CANCEL_BTN)
    return generate_inline_kb(data_with_buttons=buttons)


def get_next_role_kb(order_data: OrderOfRolesCache):
    all_roles = get_data_with_roles()
    buttons = []
    if (len(order_data["selected"]) + 1) % 4 == 0:
        if len(order_data["attacking"]) == 1:
            order_data["selected"].append("mafia")
            return get_next_role_kb(order_data)
        key = "attacking"
    else:
        key = "other"
    for role_key in order_data[key]:
        current_role = all_roles[role_key]
        buttons.append(
            InlineKeyboardButton(
                text=current_role.role, callback_data=role_key
            )
        )
    buttons.extend([SAVE_BTN, CANCEL_BTN])
    return generate_inline_kb(data_with_buttons=buttons)


CANCEL_BTN = InlineKeyboardButton(
    text="Отменить", callback_data=CANCEL_CB
)
SAVE_BTN = InlineKeyboardButton(
    text="Сохранить", callback_data=SAVE_CB
)
