from aiogram.types import InlineKeyboardButton
from keyboards.inline.builder import generate_inline_kb
from keyboards.inline.buttons.common import (
    HELP_BTN,
)
from keyboards.inline.callback_factory.settings import (
    GroupSettingsCbData,
)
from keyboards.inline.cb.cb_text import (
    TIME_FOR_DAY_CB,
    TIME_FOR_NIGHT_CB,
    VIEW_BANNED_ROLES_CB,
    VIEW_ORDER_OF_ROLES_CB,
    FOG_OF_WAR_CB,
    DIFFERENT_SETTINGS_CB,
    DURATION_OF_STAGES_CB,
)


def set_up_group_kb(group_id: int, is_there_settings: bool):
    buttons = [
        InlineKeyboardButton(
            text="Применить мои настройки",
            callback_data=GroupSettingsCbData(
                group_id=group_id, apply_own=True
            ).pack(),
        )
    ]
    if is_there_settings:
        buttons.append(
            InlineKeyboardButton(
                text="Разрешить настройки создателя",
                callback_data=GroupSettingsCbData(
                    group_id=group_id, apply_own=False
                ).pack(),
            )
        ),

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
            text="Продолжительность игровых этапов⏳",
            callback_data=DURATION_OF_STAGES_CB,
        ),
        # InlineKeyboardButton(
        #     text="Продолжительность ночи🌃",
        #     callback_data=TIME_FOR_NIGHT_CB,
        # ),
        # InlineKeyboardButton(
        #     text="Продолжительность дня🌟",
        #     callback_data=TIME_FOR_DAY_CB,
        # ),
        InlineKeyboardButton(
            text="Туман войны😶‍🌫️", callback_data=FOG_OF_WAR_CB
        ),
        InlineKeyboardButton(
            text="Больше настроек, хороших и разных‍⚙️",
            callback_data=DIFFERENT_SETTINGS_CB,
        ),
        HELP_BTN,
    ]
    return generate_inline_kb(data_with_buttons=buttons)
