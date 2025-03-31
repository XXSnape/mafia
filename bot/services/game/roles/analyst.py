from aiogram.types import InlineKeyboardButton
from cache.cache_types import GameCache
from keyboards.inline.cb.cb_text import DRAW_CB
from services.game.roles.base import ActiveRoleAtNight
from services.game.roles.base.mixins import ProcedureAfterVoting
from states.states import UserFsm
from utils.roles import get_processed_user_id_if_exists


class Analyst(ProcedureAfterVoting, ActiveRoleAtNight):
    role = "Политический аналитик"
    photo = "https://habrastorage.org/files/2e3/371/6a2/2e33716a2bb74f8eb67378334960ebb5.png"
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
    payment_for_treatment = 5
    payment_for_murder = 5

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
                text="Никого не повесят",
                callback_data=DRAW_CB,
            ),
        )
        return super().generate_markup(
            player_id=player_id,
            game_data=game_data,
            extra_buttons=extra_buttons,
        )

    @get_processed_user_id_if_exists
    async def take_action_after_voting(
        self,
        game_data: GameCache,
        removed_user: list[int],
        processed_user_id: int,
        **kwargs,
    ):
        removed_user = removed_user[0]
        url = (
            None
            if removed_user == 0
            else game_data["players"][str(removed_user)]["url"]
        )
        role = (
            None
            if removed_user == 0
            else game_data["players"][str(removed_user)][
                "pretty_role"
            ]
        )
        if processed_user_id == removed_user:
            money = 22
            to_group = "Все, кто читал прогнозы на день, были готовы к дневным событиям!"
            achievement = (
                "Удача! Действительно никого не повесили"
                if url is None
                else f"Удачный прогноз! Был повешен {url} ({role})"
            )
        else:
            money = 0
            to_group = "Обман или чёрный лебедь? Аналитические прогнозы не сбылись!"
            achievement = (
                "Неудача! Никого не повесили"
                if url is None
                else f"Неудачный прогноз! Был повешен {url} ({role})"
            )
        await self.bot.send_message(
            chat_id=game_data["game_chat"],
            text=to_group,
        )
        self.add_money_to_all_allies(
            game_data=game_data,
            money=money,
            custom_message=achievement,
            at_night=False,
        )
