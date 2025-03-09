from aiogram.types import InlineKeyboardButton

from cache.cache_types import GameCache
from keyboards.inline.builder import generate_inline_kb
from keyboards.inline.cb.cb_text import DRAW_CB
from services.roles.base import ActiveRoleAtNight
from cache.roleses import Groupings
from states.states import UserFsm


class Analyst(ActiveRoleAtNight):
    role = "Политический аналитик"
    photo = "https://habrastorage.org/files/2e3/371/6a2/2e33716a2bb74f8eb67378334960ebb5.png"
    grouping = Groupings.civilians
    purpose = "Тебе нужно на основе ранее полученных данных предсказать, кого повесят на дневном голосовании"
    do_not_choose_others = 0
    do_not_choose_self = 0
    is_self_selecting = True
    mail_message = "Кого повесят сегодня днём?"
    message_to_group_after_action = (
        "Составляется прогноз на завтрашний день"
    )
    message_to_user_after_action = (
        "Ты предположил, что повесят {url}"
    )

    def __init__(self):
        self.state_for_waiting_for_action = UserFsm.ANALYST_ASSUMES

    def generate_markup(
        self,
        player_id: int,
        game_data: GameCache,
        extra_buttons: tuple[InlineKeyboardButton, ...] = (),
    ):
        extra_buttons = (
            InlineKeyboardButton(
                text="У жителей не хватит политической воли",
                callback_data=DRAW_CB,
            ),
        )
        return super().generate_markup(
            player_id=player_id,
            game_data=game_data,
            extra_buttons=extra_buttons,
        )

    async def take_action_after_voting(
        self, game_data: GameCache, user_id: int
    ):
        predicted_id = self.get_processed_user_id(game_data)
        if not predicted_id:
            return
        analyst_id = game_data[self.roles_key][0]
        if predicted_id == user_id:
            await self.bot.send_message(
                chat_id=analyst_id, text="Прекрасная дедукция!"
            )
            await self.bot.send_message(
                chat_id=game_data["game_chat"],
                text="Все, кто читал прогнозы на день, были готовы к дневным событиям!",
            )
        else:
            await self.bot.send_message(
                chat_id=analyst_id, text="Сегодня интуиция подвела!"
            )
            await self.bot.send_message(
                chat_id=game_data["game_chat"],
                text="Обман или чёрный лебедь? Аналитические прогнозы не сбылись!",
            )
