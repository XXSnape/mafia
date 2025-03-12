from cache.cache_types import GameCache
from services.roles.base.roles import Groupings, Role
from services.roles.base import ActiveRoleAtNight
from services.roles.base.mixins import (
    MurderAfterNight,
)
from states.states import UserFsm
from utils.validators import get_processed_role_and_user_if_exists


class Killer(MurderAfterNight, ActiveRoleAtNight):
    role = "Наёмный убийца"
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
    can_kill_at_night = True
    notification_message = None
    payment_for_treatment = 0
    payment_for_murder = 13

    def __init__(self):
        self.state_for_waiting_for_action = UserFsm.KILLER_ATTACKS

    @get_processed_role_and_user_if_exists
    async def accrual_of_overnight_rewards(
        self,
        *,
        game_data: GameCache,
        all_roles: dict[str, Role],
        victims: set[int],
        processed_role: Role,
        user_url: str,
        processed_user_id: int,
    ):
        if processed_user_id not in victims:
            return
        money = processed_role.payment_for_murder * 2
        for killer_id in game_data[self.roles_key]:
            game_data["players"][str(killer_id)]["money"] += money
            game_data["players"][str(killer_id)][
                "achievements"
            ].append(
                f'Ночь {game_data["number_of_night"]}. '
                f"Убийство {user_url} ({processed_role.role}) - {money}💵"
            )

    async def mailing(self, game_data: GameCache):
        if game_data["number_of_night"] % 2 != 0:
            await super().mailing(game_data)
