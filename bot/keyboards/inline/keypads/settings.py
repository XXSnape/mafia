from operator import attrgetter

from aiogram.types import InlineKeyboardButton

from cache.cache_types import OrderOfRolesCache, RolesLiteral
from general.collection_of_roles import (
    get_data_with_roles,
    BASES_ROLES,
    REQUIRED_ROLES,
)
from keyboards.inline.builder import generate_inline_kb
from keyboards.inline.buttons.common import (
    BACK_TO_SELECTING_ACTIONS_FOR_ROLES,
    CANCEL_BTN,
    SAVE_BTN,
)
from keyboards.inline.callback_factory.settings import (
    GroupSettingsCbData,
)
from keyboards.inline.cb.cb_text import (
    VIEW_BANNED_ROLES_CB,
    EDIT_SETTINGS_CB,
    CLEAR_SETTINGS_CB,
    VIEW_ORDER_OF_ROLES_CB,
    MENU_CB,
    DELETE_LATEST_ROLE_IN_ORDER_CB,
    BAN_EVERYTHING_CB,
)
from mafia.roles import MafiaAlias
from utils.sorting import sorting_roles_by_name


def set_up_group_kb(group_id: int):
    buttons = [
        InlineKeyboardButton(
            text="Применять свои настройки",
            callback_data=GroupSettingsCbData(
                group_id=group_id, apply_own=True
            ).pack(),
        ),
        InlineKeyboardButton(
            text="Разрешить настройки создателя",
            callback_data=GroupSettingsCbData(
                group_id=group_id, apply_own=False
            ).pack(),
        ),
    ]
    return generate_inline_kb(data_with_buttons=buttons)


def select_setting_kb():
    buttons = [
        InlineKeyboardButton(
            text="Порядок ролей📋",
            callback_data=VIEW_ORDER_OF_ROLES_CB,
        ),
        InlineKeyboardButton(
            text="Забаненные роли🚫",
            callback_data=VIEW_BANNED_ROLES_CB,
        ),
        InlineKeyboardButton(
            text="Главное меню✨", callback_data=MENU_CB
        ),
    ]
    return generate_inline_kb(data_with_buttons=buttons)


def edit_roles_kb(are_there_roles: bool, to_ban: bool = False):
    buttons = [
        InlineKeyboardButton(
            text="Редактировать✏️", callback_data=EDIT_SETTINGS_CB
        )
    ]
    if are_there_roles:
        buttons.append(
            InlineKeyboardButton(
                text="Очистить все🗑️",
                callback_data=CLEAR_SETTINGS_CB,
            )
        )
    if to_ban:
        buttons.append(
            InlineKeyboardButton(
                text="Забанить все🚫",
                callback_data=BAN_EVERYTHING_CB,
            )
        )

    buttons.append(BACK_TO_SELECTING_ACTIONS_FOR_ROLES)

    return generate_inline_kb(data_with_buttons=buttons)


def suggest_banning_roles_kb(
    banned_roles_ids: list[RolesLiteral],
):
    buttons = []
    all_roles = get_data_with_roles()
    sort_keys = sorted(all_roles.keys(), key=sorting_roles_by_name)
    for key in sort_keys:
        if key in REQUIRED_ROLES:
            continue
        if key in banned_roles_ids:
            sym = "🚫"
        else:
            sym = "✅"
        buttons.append(
            InlineKeyboardButton(
                text=sym
                + all_roles[key].role
                + all_roles[key].grouping.value.name[-1],
                callback_data=key,
            )
        )

    buttons.extend([SAVE_BTN, CANCEL_BTN])
    return generate_inline_kb(
        data_with_buttons=buttons, leave_1_each=2
    )


def get_next_role_kb(
    order_data: OrderOfRolesCache, automatic_attacking: bool = True
):
    all_roles = get_data_with_roles()
    buttons = []
    leave_1_each = 1
    if (len(order_data["selected"]) + 1) % 4 == 0:
        if automatic_attacking and len(order_data["attacking"]) == 1:
            order_data["selected"].append(MafiaAlias.role_id)
            return get_next_role_kb(order_data)
        key = "attacking"
    else:
        key = "other"
    for role_key in order_data[key]:
        current_role = all_roles[role_key]
        buttons.append(
            InlineKeyboardButton(
                text=current_role.role
                + current_role.grouping.value.name[-1],
                callback_data=role_key,
            )
        )
    buttons.sort(key=attrgetter("text"))
    if len(order_data["selected"]) > 4:
        buttons.extend(
            [
                InlineKeyboardButton(
                    text="🗑️Убрать последний",
                    callback_data=DELETE_LATEST_ROLE_IN_ORDER_CB,
                ),
                SAVE_BTN,
            ]
        )
        leave_1_each = 3
    buttons.append(CANCEL_BTN)
    return generate_inline_kb(
        data_with_buttons=buttons, leave_1_each=leave_1_each
    )
