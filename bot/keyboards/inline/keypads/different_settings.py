from aiogram.types import InlineKeyboardButton

from cache.cache_types import DifferentSettingsCache
from keyboards.inline.builder import generate_inline_kb
from keyboards.inline.buttons.common import (
    BACK_TO_SELECTING_ACTIONS_ON_SETTINGS_BTN,
)
from keyboards.inline.cb import cb_text
from keyboards.inline.cb.cb_text import (
    SHOW_ROLES_AFTER_DEATH_CB,
    SHOW_PEACEFUL_ALLIES_CB,
)


def check_for_settings(
    buttons: list[InlineKeyboardButton],
    different_settings: DifferentSettingsCache,
):
    for btn in buttons:
        if different_settings[btn.callback_data]:
            btn.text += "✅"
        else:
            btn.text += "❌"


def get_for_of_war_buttons():
    return (
        InlineKeyboardButton(
            text="Показывать роли погибших",
            callback_data=SHOW_ROLES_AFTER_DEATH_CB,
        ),
        InlineKeyboardButton(
            text="Показывать мирным своих заместителей",
            callback_data=SHOW_PEACEFUL_ALLIES_CB,
        ),
        InlineKeyboardButton(
            text="Показывать имена во время голосования",
            callback_data=cb_text.SHOW_USERNAMES_DURING_VOTING_CB,
        ),
        InlineKeyboardButton(
            text="Показывать имена после подтверждения",
            callback_data=cb_text.SHOW_USERNAMES_AFTER_CONFIRMATION_CB,
        ),
        InlineKeyboardButton(
            text="Показывать роли ночных убийц",
            callback_data=cb_text.SHOW_KILLERS_CB,
        ),
        InlineKeyboardButton(
            text="Писать в личку о ночных гостях",
            callback_data=cb_text.SHOW_INFORMATION_ABOUT_GUESTS_AT_NIGHT_CB,
        ),
    )


def get_different_settings_buttons():
    return (
        InlineKeyboardButton(
            text="Можно убивать сокомандников",
            callback_data=cb_text.CAN_KILL_TEAMMATES_CB,
        ),
        InlineKeyboardButton(
            text="Маршал может убивать ночью",
            callback_data=cb_text.CAN_MARSHAL_KILL_CB,
        ),
        InlineKeyboardButton(
            text="Мафией будет каждый 3-ий игрок",
            callback_data=cb_text.MAFIA_EVERY_3_CB,
        ),
    )


def fog_of_war_options_kb(fog_of_war: DifferentSettingsCache):
    buttons = [
        *get_for_of_war_buttons(),
        BACK_TO_SELECTING_ACTIONS_ON_SETTINGS_BTN,
    ]
    check_for_settings(
        buttons=buttons[:-1], different_settings=fog_of_war
    )
    return generate_inline_kb(data_with_buttons=buttons)


def different_options_kb(different_settings: DifferentSettingsCache):
    buttons = [
        *get_different_settings_buttons(),
        BACK_TO_SELECTING_ACTIONS_ON_SETTINGS_BTN,
    ]
    check_for_settings(
        buttons=buttons[:-1], different_settings=different_settings
    )
    return generate_inline_kb(data_with_buttons=buttons)
