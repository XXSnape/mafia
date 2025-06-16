from aiogram.types import InlineKeyboardButton

from general.resources import Resources, get_data_about_resource
from keyboards.inline.builder import generate_inline_kb
from keyboards.inline.callback_factory.shop import (
    ChooseToPurchaseCbData,
)


def available_resources_kb():
    buttons = []
    for resource in Resources:
        asset = get_data_about_resource(resource)
        btn = InlineKeyboardButton(
            text=asset.name,
            callback_data=ChooseToPurchaseCbData(
                resource=resource
            ).pack(),
        )
        buttons.append(btn)
    return generate_inline_kb(data_with_buttons=buttons)
