from cache.cache_types import GameCache, ExtraCache
from mafia.roles.base.mixins import ProcedureAfterNight
from mafia.roles.base.roles import Role
from general.groupings import Groupings
from general.text import ROLE_IS_KNOWN
from mafia.roles.base import ActiveRoleAtNight
from states.states import UserFsm
from utils.roles import get_processed_role_and_user_if_exists


class Traitor(ProcedureAfterNight, ActiveRoleAtNight):
    role = "Госизменщик"
    role_id = "traitor"
    photo = "https://i.playground.ru/p/sLHLRFjDy8_89wYe26RIQw.jpeg"
    grouping = Groupings.criminals
    need_to_monitor_interaction = False
    purpose = "Ты можешь просыпаться каждую 2-ую ночь и узнавать роль других игроков для мафии."
    message_to_group_after_action = (
        "Мафия и Даркнет. Что может сочетаться лучше? "
        "Поддельные ксивы помогают узнавать правду!"
    )
    message_to_user_after_action = "Ты выбрал узнать роль {url}"
    mail_message = "Кого проверишь для мафии?"
    notification_message = ROLE_IS_KNOWN
    payment_for_treatment = 0
    payment_for_murder = 15
    extra_data = [
        ExtraCache(
            key="mafias_are_shown",
            need_to_clear=False,
            data_type=str,
        )
    ]

    def __init__(self):
        self.state_for_waiting_for_action = UserFsm.TRAITOR_FINDS_OUT

    def cancel_actions(self, **kwargs):
        return False

    async def procedure_after_night(self, **kwargs):
        pass

    @get_processed_role_and_user_if_exists
    async def accrual_of_overnight_rewards(
        self,
        game_data: GameCache,
        processed_role: Role,
        user_url: str,
        processed_user_id: int,
        **kwargs,
    ):
        self.add_money_to_all_allies(
            game_data=game_data,
            money=10,
            beginning_message="Проверка",
            user_url=user_url,
            processed_role=processed_role,
        )
