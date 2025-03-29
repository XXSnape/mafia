from functools import partial

from aiogram.types import InlineKeyboardButton

from keyboards.inline.builder import generate_inline_kb


def get_to_bot_kb(text="Ознакомиться с ролью"):
    return generate_inline_kb(
        data_with_buttons=[
            InlineKeyboardButton(
                text=text, url="t.me/Drivenicebot"
            )  # TODO SETTINGS
        ]
    )


participate_in_social_life = partial(
    get_to_bot_kb, text="Участвовать в социальной жизни!"
)
