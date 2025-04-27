from aiogram.types import InlineKeyboardButton
from keyboards.inline.builder import generate_inline_kb
from keyboards.inline.buttons.common import (
    BACK_TO_SELECTING_ACTIONS_ON_SETTINGS_BTN,
    HELP_BTN,
)
from keyboards.inline.callback_factory.settings import (
    GroupSettingsCbData,
    TimeOfDay,
    TimeOfDayCbData,
)
from keyboards.inline.cb.cb_text import (
    BAN_EVERYTHING_CB,
    EDIT_SETTINGS_CB,
    LENGTH_OF_DAY_CB,
    LENGTH_OF_NIGHT_CB,
    VIEW_BANNED_ROLES_CB,
    VIEW_ORDER_OF_ROLES_CB,
    FOG_OF_WAR_CB,
    DIFFERENT_SETTINGS_CB,
)


def adjust_time_kb(current_time: int, time_of_day: TimeOfDay):
    buttons = []
    for seconds in range(45, 121, 15):
        text = str(seconds)
        if current_time == seconds:
            text = "✅" + text
        buttons.append(
            InlineKeyboardButton(
                text=text,
                callback_data=TimeOfDayCbData(
                    time_of_day=time_of_day, seconds=seconds
                ).pack(),
            )
        )
    buttons.append(BACK_TO_SELECTING_ACTIONS_ON_SETTINGS_BTN)
    return generate_inline_kb(
        data_with_buttons=buttons, leave_1_each=1
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
            text="Продолжительность ночи🌃",
            callback_data=LENGTH_OF_NIGHT_CB,
        ),
        InlineKeyboardButton(
            text="Продолжительность дня🌟",
            callback_data=LENGTH_OF_DAY_CB,
        ),
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
