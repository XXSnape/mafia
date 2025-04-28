from collections.abc import Iterable

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def generate_inline_kb(
    data_with_buttons=(),
    sizes: Iterable[int] = (1,),
    leave_1_each: int | None = None,
    row: int = 2,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for data in data_with_buttons:
        if data:
            builder.add(data)
    if leave_1_each:
        sizes = [
            *[row]
            * ((len(data_with_buttons) - leave_1_each) // row),
            1,
        ]
    builder.adjust(*sizes)
    return builder.as_markup()
