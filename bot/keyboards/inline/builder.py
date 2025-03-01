from collections.abc import Iterable

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def generate_inline_kb(
    data_with_url=(),
    data_with_buttons=(),
    data_with_cb=(),
    sizes: Iterable[int] = (1,),
) -> InlineKeyboardMarkup:
    """
    Генерирует клавиатуру по различным данным
    :param data_with_url: итерируемый объект с названием и url
    :param data_with_buttons: итерируемый объект с готовыми кнопками
    :param data_with_cb: итерируемый объект с текстом и данными
    :param sizes: расположение кнопок
    :return: InlineKeyboardMarkup
    """
    builder = InlineKeyboardBuilder()
    for data in data_with_buttons:
        if data:
            builder.add(data)
    for data in data_with_url:
        builder.button(text=data[0], url=data[1])

    for data in data_with_cb:
        builder.button(text=data[0], callback_data=data[1])
    builder.adjust(*sizes)
    return builder.as_markup()
