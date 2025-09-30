from aiogram.types import InlineKeyboardButton
from cache.cache_types import GameCache, RolesLiteral, UserIdInt
from general.groupings import Groupings
from keyboards.inline.cb.cb_text import DRAW_CB
from states.game import UserFsm
from utils.roles import (
    get_processed_user_id_if_exists,
)

from mafia.roles.base import ActiveRoleAtNightABC
from mafia.roles.base.mixins import (
    ProcedureAfterVotingABC,
    SpecialMoneyManagerMixin,
)
from mafia.roles.descriptions.description import RoleDescription
from mafia.roles.descriptions.texts import (
    CAN_CHOOSE_YOURSELF,
    DONT_PAY_FOR_VOTING,
)


class Analyst(
    SpecialMoneyManagerMixin,
    ProcedureAfterVotingABC,
    ActiveRoleAtNightABC,
):
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
    number_in_order_after_voting = 3
    extra_buttons = (
        InlineKeyboardButton(
            text="Никого не повесят",
            callback_data=DRAW_CB,
        ),
    )
    final_mission = "Угадать {count} раз(а)"
    divider = 2
    payment_for_successful_operation = 15

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
            f"всего, деленное на {self.divider}. "
            f"Например, если играют 5 человек, нужно сделать {5 // self.divider} "
            f"верных прогноза, если 8, тогда {8 // self.divider} и т.д.",
        )

    def cancel_actions(self, game_data: GameCache, user_id: int):
        if self.get_processed_user_id(game_data) == 0:
            game_data[self.processed_users_key].clear()
            return True
        return super().cancel_actions(
            game_data=game_data, user_id=user_id
        )

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
            self.successful_actions += 1
            money = 10
            achievement = (
                "Удача! Действительно никого не повесили"
                if url is None
                else f"Удачный прогноз! Был повешен {url} ({role})"
            )
        else:
            money = 0
            achievement = (
                "Неудача! Никого не повесили"
                if url is None
                else f"Неудачный прогноз! Был повешен {url} ({role})"
            )
        self.add_money_to_all_allies(
            game_data=game_data,
            money=money,
            custom_message=achievement,
            at_night=False,
        )
