from aiogram import Bot
from aiogram.types import InlineKeyboardButton

from keyboards.inline.builder import generate_inline_kb
from keyboards.inline.buttons.common import (
    get_join_to_game_btn,
    opt_out_of_notifications_btn,
)
from keyboards.inline.callback_factory.subscriptions import (
    GameNotificationCbData,
)


async def newsletter_about_new_game(
    bot: Bot, game_chat: int, group_id: int
):
    buttons = [
        await get_join_to_game_btn(bot=bot, game_chat=game_chat),
        opt_out_of_notifications_btn(group_id=group_id),
    ]
    return generate_inline_kb(data_with_buttons=buttons)
