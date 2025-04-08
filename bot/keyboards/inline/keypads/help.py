from operator import attrgetter

from aiogram.types import InlineKeyboardButton

from general.collection_of_roles import get_data_with_roles
from keyboards.inline.builder import generate_inline_kb
from keyboards.inline.buttons.common import HELP_BTN
from keyboards.inline.callback_factory.help import RoleCbData
from keyboards.inline.cb.cb_text import VIEW_ROLES_CB


def get_roles_kb():
    all_roles = get_data_with_roles()
    buttons = [
        InlineKeyboardButton(
            text=role.role + role.grouping.value.name[-1],
            callback_data=RoleCbData(role_id=role_id).pack(),
        )
        for role_id, role in all_roles.items()
    ]
    buttons.sort(key=attrgetter("text"))
    buttons.append(HELP_BTN)
    return generate_inline_kb(
        data_with_buttons=buttons, leave_1_each=1
    )


def help_options_kb():
    buttons = [
        InlineKeyboardButton(
            text="Роли🎭", callback_data=VIEW_ROLES_CB
        )
    ]
    return generate_inline_kb(data_with_buttons=buttons)


def go_back_to_options_kb():
    buttons = [
        InlineKeyboardButton(
            text="К ролям🎭", callback_data=VIEW_ROLES_CB
        ),
        HELP_BTN,
    ]
    return generate_inline_kb(data_with_buttons=buttons)
