from aiogram.types import InlineKeyboardButton

from general.resources import Resources
from keyboards.inline.builder import generate_inline_kb
from keyboards.inline.callback_factory.shop import (
    ChooseToPurchaseCbData,
)


def available_resources_kb():
    buttons = [
        InlineKeyboardButton(
            text="💌Анонимки",
            callback_data=ChooseToPurchaseCbData(
                resource=Resources.anonymous_letters
            ).pack(),
        )
    ]
    return generate_inline_kb(data_with_buttons=buttons)
