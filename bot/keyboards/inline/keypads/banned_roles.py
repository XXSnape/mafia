from aiogram.types import InlineKeyboardButton

from cache.cache_types import RolesLiteral
from general.collection_of_roles import (
    get_data_with_roles,
    REQUIRED_ROLES,
    BASES_ROLES,
)
from general.text import TO_SAVE
from keyboards.inline.builder import generate_inline_kb
from keyboards.inline.buttons.common import (
    CANCEL_BTN,
    BACK_TO_SELECTING_ACTIONS_ON_SETTINGS_BTN,
)
from keyboards.inline.callback_factory.help import BannedRolesCbData
from keyboards.inline.cb.cb_text import (
    EDIT_BANNED_ROLES_CB,
    CLEAR_BANNED_ROLES_CB,
    BAN_EVERYTHING_CB,
    SAVE_ORDER_OF_ROLES_CB,
    SAVE_BANNED_ROLES_CB,
)
from utils.sorting import sorting_roles_by_name


def edit_banned_roles_kb(banned_roles_ids: list[RolesLiteral]):
    buttons = [
        InlineKeyboardButton(
            text="Редактировать✏️", callback_data=EDIT_BANNED_ROLES_CB
        )
    ]
    if banned_roles_ids:
        buttons.append(
            InlineKeyboardButton(
                text="Очистить все🗑️",
                callback_data=CLEAR_BANNED_ROLES_CB,
            )
        )
    if len(banned_roles_ids) != len(get_data_with_roles()) - len(
        REQUIRED_ROLES
    ):
        buttons.append(
            InlineKeyboardButton(
                text="Забанить все🚫",
                callback_data=BAN_EVERYTHING_CB,
            )
        )
    buttons.append(BACK_TO_SELECTING_ACTIONS_ON_SETTINGS_BTN)
    return generate_inline_kb(data_with_buttons=buttons)


def suggest_banning_roles_kb(
    banned_roles_ids: list[RolesLiteral],
):
    buttons = []
    all_roles = get_data_with_roles()
    sort_keys = sorted(all_roles.keys(), key=sorting_roles_by_name)
    for role_id in sort_keys:
        if role_id in REQUIRED_ROLES:
            continue
        if role_id in banned_roles_ids:
            sym = "🚫"
        else:
            sym = "✅"
        buttons.append(
            InlineKeyboardButton(
                text=sym
                + all_roles[role_id].role
                + all_roles[role_id].grouping.value.name[-1],
                callback_data=BannedRolesCbData(
                    role_id=role_id
                ).pack(),
            )
        )

    buttons.extend(
        [
            InlineKeyboardButton(
                text=TO_SAVE, callback_data=SAVE_BANNED_ROLES_CB
            ),
            CANCEL_BTN,
        ]
    )
    return generate_inline_kb(
        data_with_buttons=buttons, leave_1_each=2
    )
