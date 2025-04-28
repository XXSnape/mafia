from aiogram.types import InlineKeyboardButton

from cache.cache_types import StagesOfGameLiteral
from keyboards.inline.builder import generate_inline_kb
from keyboards.inline.buttons.common import (
    BACK_TO_SELECTING_ACTIONS_ON_SETTINGS_BTN,
    CANCEL_BTN,
)
from keyboards.inline.callback_factory.settings import (
    TimeOfDayCbData,
)
from keyboards.inline.cb.cb_text import (
    TIME_FOR_NIGHT_CB,
    TIME_FOR_DAY_CB,
    TIME_FOR_VOTING_CB,
    TIME_FOR_CONFIRMATION_CB,
)
from utils.pretty_text import get_minutes_and_seconds_text


def select_stage_of_game_kb():
    buttons = [
        InlineKeyboardButton(
            text="Продолжительность ночи🌃",
            callback_data=TIME_FOR_NIGHT_CB,
        ),
        InlineKeyboardButton(
            text="Продолжительность дня🌟",
            callback_data=TIME_FOR_DAY_CB,
        ),
        InlineKeyboardButton(
            text="Продолжительность голосования🗳",
            callback_data=TIME_FOR_VOTING_CB,
        ),
        InlineKeyboardButton(
            text="Продолжительность подтверждения✔️",
            callback_data=TIME_FOR_CONFIRMATION_CB,
        ),
        CANCEL_BTN,
    ]
    return generate_inline_kb(data_with_buttons=buttons)


def adjust_time_kb(
    current_time: int, stage_of_game: StagesOfGameLiteral
):
    buttons = []
    for seconds in [
        30,
        35,
        40,
        45,
        55,
        65,
        80,
        100,
        120,
        150,
        180,
        200,
    ]:
        text = get_minutes_and_seconds_text(
            seconds=seconds, message=""
        )
        if current_time == seconds:
            text = "✅" + text
        buttons.append(
            InlineKeyboardButton(
                text=text,
                callback_data=TimeOfDayCbData(
                    stage_of_game=stage_of_game, seconds=seconds
                ).pack(),
            )
        )
    buttons.append(BACK_TO_SELECTING_ACTIONS_ON_SETTINGS_BTN)
    return generate_inline_kb(
        data_with_buttons=buttons, leave_1_each=1, row=3
    )
