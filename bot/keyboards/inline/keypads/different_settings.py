from aiogram.types import InlineKeyboardButton

from cache.cache_types import DifferentSettingsCache
from keyboards.inline.builder import generate_inline_kb
from keyboards.inline.buttons.common import (
    BACK_TO_SELECTING_ACTIONS_ON_SETTINGS_BTN,
)
from keyboards.inline.cb import cb_text


def check_for_settings(
    buttons: list[InlineKeyboardButton],
    different_settings: DifferentSettingsCache,
):
    for btn in buttons[:-1]:
        if different_settings[btn.callback_data]:
            btn.text += "✅"
        else:
            btn.text += "🚫"


def fog_of_war_options_kb(fog_of_war: DifferentSettingsCache):
    buttons = [
        InlineKeyboardButton(
            text="Показывать роли умерших ночью",
            callback_data=cb_text.SHOW_DEAD_ROLES_AFTER_NIGHT_CB,
        ),
        InlineKeyboardButton(
            text="Показывать роли умерших днём",
            callback_data=cb_text.SHOW_DEAD_ROLES_AFTER_HANGING_CB,
        ),
        InlineKeyboardButton(
            text="Показывать роли умерших из-за неактивности",
            callback_data=cb_text.SHOW_ROLES_DIED_DUE_TO_INACTIVITY_CB,
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
        BACK_TO_SELECTING_ACTIONS_ON_SETTINGS_BTN,
    ]
    check_for_settings(
        buttons=buttons, different_settings=fog_of_war
    )
    return generate_inline_kb(data_with_buttons=buttons)


def different_options_kb(different_settings: DifferentSettingsCache):
    buttons = [
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
        BACK_TO_SELECTING_ACTIONS_ON_SETTINGS_BTN,
    ]
    check_for_settings(
        buttons=buttons, different_settings=different_settings
    )
    return generate_inline_kb(data_with_buttons=buttons)
