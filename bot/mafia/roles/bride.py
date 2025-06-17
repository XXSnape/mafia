from random import choice

from cache.cache_types import GameCache, RolesLiteral, UserIdInt
from cache.extra import ExtraCache
from general.groupings import Groupings
from general.text import (
    ROLE_IS_KNOWN,
)
from mafia.roles.base import ActiveRoleAtNightABC
from mafia.roles.base.mixins import (
    MafiaConverterABC,
    ProcedureAfterNightABC,
    ObligatoryKillerABC,
)
from mafia.roles.descriptions.description import RoleDescription
from mafia.roles.descriptions.texts import (
    CAN_CHOOSE_YOURSELF,
)
from states.game import UserFsm
from utils.roles import get_processed_user_id_if_exists


class Bride(
    ObligatoryKillerABC, ProcedureAfterNightABC, ActiveRoleAtNightABC
):
    role = "Кровавая невеста"
    role_id: RolesLiteral = "bride"
    grouping = Groupings.other
    purpose = "Обязательно в первую ночь выбери жениха и делай все, чтобы он просто остался живым"
    message_to_group_after_action = (
        "Заключить брак любой может, но все ли умрут в один день?"
    )
    photo = "https://i.pinimg.com/736x/34/2b/eb/342bebbc1da7ac2937fc7555cc1e0e7f.jpg"
    mail_message = "Кого возьмешь в мужья?"
    message_to_user_after_action = (
        "Твой выбор пал на свадьбу с {url}"
    )
    need_to_monitor_interaction = False
    notification_message = None
    payment_for_treatment = 5
    payment_for_murder = 13

    @property
    def role_description(self) -> RoleDescription:
        return RoleDescription(
            skill="В начале игры выбирает жениха (иначе проигрывает сразу) "
            "и оставшееся время делает всё возможное, чтобы суженый выжил. "
            "Если его убьют, Невеста так же умирает до наступления следующей ночи. "
            "Если Невесту убьют раньше, каждую 2ую ночь случайным образом будут умирать жители города, но не жених. "
            "Это прекратится, когда погибнет избранник.",
            pay_for=[
                "Количество ночей, прожитых женихом, если он выжил"
            ],
            wins_if="Жених должен выжить",
        )

    @get_processed_user_id_if_exists
    async def procedure_after_night(
        self, processed_user_id: UserIdInt, **kwargs
    ):
        self.groom_id = processed_user_id
        print("procedure_after_night", self.groom_id)

    @staticmethod
    def allow_sending_mailing(game_data: GameCache):
        return game_data["number_of_night"] == 1

    async def accrual_of_overnight_rewards(self, **kwargs):
        return

    def kill_after_all_actions(
        self, game_data: GameCache
    ) -> tuple[UserIdInt, str] | None:
        print(self.groom_id, game_data[self.roles_key])
        if self.groom_id is None and game_data[self.roles_key]:
            return (
                game_data[self.roles_key][0],
                "Жениха выбирать обязательно!",
            )
        if (
            self.groom_id not in game_data["live_players_ids"]
            and game_data[self.roles_key]
        ):
            return (
                game_data[self.roles_key][0],
                "К сожалению, твой жених погиб, а ты с ним!",
            )
        if (
            not game_data[self.roles_key]
            and self.groom_id in game_data["live_players_ids"]
        ):
            players = [
                user_id
                for user_id in game_data["live_players_ids"]
                if user_id != self.groom_id
            ]
            return (
                choice(players),
                "К сожалению, тебя убил дух разъярённой невесты",
            )
        return None

    def cancel_actions(
        self, game_data: GameCache, user_id: UserIdInt
    ):
        return False

    def __init__(self):
        self.state_for_waiting_for_action = UserFsm.BRIDE_CHOOSES
        self.groom_id: UserIdInt | None = None
