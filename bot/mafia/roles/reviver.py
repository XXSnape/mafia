from cache.cache_types import RolesLiteral, UserIdInt, GameCache
from general.groupings import Groupings
from mafia.roles import ActiveRoleAtNightABC
from mafia.roles.base.mixins import (
    FinisherOfNight,
    ProcedureAfterVotingABC,
)
from mafia.roles.descriptions.description import RoleDescription
from states.game import UserFsm
from utils.roles import get_processed_user_id_if_exists


class Reviver(
    FinisherOfNight,
    ProcedureAfterVotingABC,
    ActiveRoleAtNightABC,
):
    # врача и маршала не заменять
    role = "Воскреситель"
    role_id: RolesLiteral = "reviver"
    grouping = Groupings.civilians
    purpose = (
        f"Если погибнут все маршалы или врачи, "
        f"сможешь выбрать любого игрока, "
        f"и, если его группировка {Groupings.civilians.name}, "
        f"он станет маршалом или врачом"
    )
    message_to_group_after_action = None
    photo = (
        "https://media.2x2tv.ru/content"
        "/images/size/w1440h1080/2024/03/megamiiiiiindtwocoveeeer.jpg"
    )
    mail_message = "Кого попытаешься превратить в маршала или врача?"
    need_to_monitor_interaction = False
    payment_for_treatment = 12
    payment_for_murder = 14

    @property
    def role_description(self) -> RoleDescription:
        return RoleDescription(
            skill="Если в игре не осталось маршала или врача, "
            "тогда выбирает их заместителя. Если после ночи и голосования "
            "заместитель остается жив, то он становится маршалом или доктором.",
            pay_for=["Перевоплощения в маршала или доктора"],
            limitations=[
                f"Можно перевоплощать только членов группировки {Groupings.civilians.value.name}",
                "Если выбранная цель является врачом, или маршалом, или их союзником, "
                "её перевоплотить нельзя. "
                "Другими словами, если в игре нет маршала, доктор не сможет занять его место, и наоборот",
            ],
            features=[
                "В случае, если в игре нет ни маршалов, ни докторов, выбранный заместитель превращается в маршала"
            ],
        )

    def __init__(self):
        self.state_for_waiting_for_action = (
            UserFsm.RESURRECTOR_REVIVES
        )
        self.reborn_id: UserIdInt | None = None

    @get_processed_user_id_if_exists
    async def take_action_after_voting(
        self,
        game_data: GameCache,
        processed_user_id: UserIdInt,
        **kwargs,
    ):
        self.reborn_id = processed_user_id

    @staticmethod
    def allow_sending_mailing(game_data: GameCache) -> bool:
        from .policeman import Policeman
        from .doctor import Doctor

        return (not game_data[Policeman.roles_key]) and (
            not game_data[Doctor.roles_key]
        )

    async def end_night(self, game_data: GameCache):
        pass
