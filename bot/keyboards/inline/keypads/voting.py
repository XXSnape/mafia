from aiogram.types import InlineKeyboardButton

from cache.cache_types import PlayersIds
from keyboards.inline.builder import generate_inline_kb
from keyboards.inline.callback_factory.recognize_user import (
    AimedUserCbData,
    ProsAndCons,
)


def get_vote_for_aim_kb(
    user_id: int, pros: PlayersIds, cons: PlayersIds
):
    buttons = [
        InlineKeyboardButton(
            text=f"Вешаем нелюдя🤬 ({len(pros)})",
            callback_data=AimedUserCbData(
                user_id=user_id, action=ProsAndCons.pros
            ).pack(),
        ),
        InlineKeyboardButton(
            text=f"Бережём наше сокровище🥹 ({len(cons)})",
            callback_data=AimedUserCbData(
                user_id=user_id, action=ProsAndCons.cons
            ).pack(),
        ),
    ]
    return generate_inline_kb(data_with_buttons=buttons)
