from aiogram.types import InlineKeyboardButton
from cache.cache_types import GameCache, RolesLiteral, UserIdInt
from general import settings
from general.groupings import Groupings
from keyboards.inline.cb.cb_text import DRAW_CB
from mafia.roles.base import ActiveRoleAtNightABC
from mafia.roles.base.mixins import ProcedureAfterVotingABC
from mafia.roles.descriptions.description import RoleDescription
from mafia.roles.descriptions.texts import (
    CAN_CHOOSE_YOURSELF,
    DONT_PAY_FOR_VOTING,
)
from states.game import UserFsm
from utils.roles import (
    get_processed_user_id_if_exists,
)


class Analyst(ProcedureAfterVotingABC, ActiveRoleAtNightABC):
    role = "Политический аналитик"
    role_id: RolesLiteral = "analyst"
    grouping = Groupings.other
    photo = "https://habrastorage.org/files/2e3/371/6a2/2e33716a2bb74f8eb67378334960ebb5.png"
    purpose = "Тебе нужно на основе ранее полученных данных предсказать, кого повесят на дневном голосовании"
    do_not_choose_others = 0
    do_not_choose_self = 0
    is_self_selecting = True
    need_to_monitor_interaction = False
    mail_message = "Кого повесят сегодня днём?"
    message_to_group_after_action = (
        "Составляется прогноз на завтрашний день"
    )
    message_to_user_after_action = (
        "Ты предположил, что повесят {url}"
    )
    payment_for_treatment = 5
    payment_for_murder = 5
    number_in_order_after_voting = 2

    @property
    def role_description(self) -> RoleDescription:
        return RoleDescription(
            skill="Делает прогноз на игрока, которого должны повесить днём",
            pay_for=["Верный прогноз"],
            features=[
                "Может выбрать вариант, что никого не повесят",
                CAN_CHOOSE_YOURSELF,
            ],
            limitations=[DONT_PAY_FOR_VOTING],
            wins_if="Сделать столько прогнозов, сколько равняется количество игроков "
            "всего, деленное на 2. "
            "Например, если играют 5 человек, нужно сделать 2 верных прогноза, если 8, тогда 4 и т.д.",
        )

    def __init__(self):
        self.state_for_waiting_for_action = UserFsm.ANALYST_ASSUMES
        self.number_of_predictions = 0
        self.necessary_to_win: int | None = None

    def introducing_users_to_roles(self, game_data: GameCache):
        self.necessary_to_win = (
            len(game_data["live_players_ids"]) // 2
        )
        self.purpose = f"{self.purpose}\n\nДля победы нужно угадать {self.necessary_to_win} раз(а)"
        return super().introducing_users_to_roles(
            game_data=game_data
        )

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

    def cancel_actions(self, game_data: GameCache, user_id: int):
        if self.get_processed_user_id(game_data) == 0:
            game_data[self.processed_users_key].clear()
            return True
        return super().cancel_actions(
            game_data=game_data, user_id=user_id
        )

    def get_money_for_victory_and_nights(
        self,
        game_data: GameCache,
        **kwargs,
    ):
        if self.number_of_predictions >= self.necessary_to_win:
            payment = (
                15
                * (
                    len(game_data["players"])
                    // settings.mafia.minimum_number_of_players
                )
                * self.number_of_predictions
            )
            return payment, 0
        return 0, 0

    @get_processed_user_id_if_exists
    async def take_action_after_voting(
        self,
        game_data: GameCache,
        removed_user: list[int],
        processed_user_id: UserIdInt,
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
            self.number_of_predictions += 1
            money = 10
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
        if game_data["settings"]["show_roles_after_death"]:
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
