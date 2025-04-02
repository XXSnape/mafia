from cache.cache_types import GameCache
from mafia.roles.base.roles import Role
from general.groupings import Groupings
from mafia.roles.base import ActiveRoleAtNight
from mafia.roles.base.mixins import (
    MurderAfterNight,
)
from states.states import UserFsm
from utils.roles import get_processed_role_and_user_if_exists


class Killer(MurderAfterNight, ActiveRoleAtNight):
    role = "Наёмный убийца"
    role_id = "killer"
    need_to_monitor_interaction = False
    photo = (
        "https://steamuserimages-a.akamaihd.net/ugc/633105202506112549/988D"
        "53D1D6BF2FAC4665E453F736C438F601DF6D/"
        "?imw=512&imh=512&ima=fit&impolicy=Letterbox&imcolor=%23000000&letterbox=true"
    )
    grouping = Groupings.killer
    purpose = "Ты убиваешь, кого захочешь, а затем восстанавливаешь свои силы целую ночь."
    message_to_group_after_action = (
        "ЧВК продолжают работать на территории города!"
    )
    message_to_user_after_action = "Ты решился ликвидировать {url}"
    mail_message = "Реши, кому поможешь этой ночью решить проблемы и убить врага!"
    payment_for_treatment = 0
    payment_for_murder = 13

    def __init__(self):
        self.state_for_waiting_for_action = UserFsm.KILLER_ATTACKS

    @get_processed_role_and_user_if_exists
    async def accrual_of_overnight_rewards(
        self,
        game_data: GameCache,
        victims: set[int],
        processed_role: Role,
        user_url: str,
        processed_user_id: int,
        **kwargs
    ):
        if processed_user_id not in victims:
            return
        money = processed_role.payment_for_murder * 2
        self.add_money_to_all_allies(
            game_data=game_data,
            money=money,
            user_url=user_url,
            processed_role=processed_role,
            beginning_message="Убийство",
        )

    @staticmethod
    def allow_sending_mailing(game_data: GameCache):
        from mafia.roles import Mafia

        if (
            game_data["number_of_night"] % 2 != 0
            or not game_data[Mafia.roles_key]
        ):
            return True
