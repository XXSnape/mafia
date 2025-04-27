from aiogram.types import InlineKeyboardButton

from cache.cache_types import DifferentSettingsCache
from keyboards.inline.builder import generate_inline_kb
from keyboards.inline.buttons.common import (
    BACK_TO_SELECTING_ACTIONS_ON_SETTINGS_BTN,
)
from keyboards.inline.cb import cb_text


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
            text="Показывать роли ночных убийц",
            callback_data=cb_text.SHOW_KILLERS_CB,
        ),
        InlineKeyboardButton(
            text="Сбрасывать полезную информацию в чат",
            callback_data=cb_text.SHOW_INFORMATION_IN_SHARED_CHAT_CB,
        ),
        InlineKeyboardButton(
            text="Писать в личку о ночных гостях",
            callback_data=cb_text.SHOW_INFORMATION_ABOUT_GUESTS_AT_NIGHT_CB,
        ),
        BACK_TO_SELECTING_ACTIONS_ON_SETTINGS_BTN,
    ]
    for btn in buttons[:-1]:
        if fog_of_war[btn.callback_data]:
            btn.text += "✅"
        else:
            btn.text += "🚫"
    return generate_inline_kb(data_with_buttons=buttons)
