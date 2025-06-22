from cache.cache_types import GameCache, RolesLiteral, UserIdInt
from general.groupings import Groupings
from mafia.roles import RoleABC
from mafia.roles.base import ActiveRoleAtNightABC
from mafia.roles.base.mixins import ProcedureAfterVotingABC
from mafia.roles.descriptions.description import RoleDescription
from mafia.roles.descriptions.texts import (
    CANT_CHOOSE_IN_ROW,
)
from utils.roles import (
    get_processed_role_and_user_if_exists,
    get_user_role_and_url,
)


class Manager(ProcedureAfterVotingABC, ActiveRoleAtNightABC):
    role = "Распорядитель"
    role_id: RolesLiteral = "manager"
    grouping = Groupings.civilians
    photo = "https://cdn1.ozone.ru/s3/multimedia-h/6125881757.jpg"
    purpose = "Ты должен грамотно выбирать людей, которые на голосовании будут иметь 2 голоса"
    mail_message = "Кому дашь право голосовать дважды?"
    message_to_group_after_action = (
        "Двойные стандарты? Да! "
        "У кого-то теперь больше прав и возможностей днём. Не приманит ли это мафию?"
    )
    message_to_user_after_action = (
        "Ты дал право {url} голосовать дважды"
    )
    payment_for_treatment = 7
    payment_for_murder = 8

    @property
    def role_description(self) -> RoleDescription:
        return RoleDescription(
            skill="Даёт право голосовать любому игроку дважды",
            pay_for=[
                "Голоса, отданные избраннику, "
                "если он проголосовал против враждебной или нейтральной группировки"
            ],
            limitations=[CANT_CHOOSE_IN_ROW],
        )

    @get_processed_role_and_user_if_exists
    async def take_action_after_voting(
        self,
        game_data: GameCache,
        processed_role: RoleABC,
        processed_user_id: UserIdInt,
        user_url: str,
        **kwargs,
    ):
        for user_id, victim_id in game_data["vote_for"]:
            if user_id == processed_user_id:
                role, url = get_user_role_and_url(
                    game_data=game_data,
                    processed_user_id=victim_id,
                    all_roles=self.all_roles,
                )
                if role.grouping == Groupings.civilians:
                    money = 0
                else:
                    money = role.payment_for_murder // 2
                self.add_money_to_all_allies(
                    game_data=game_data,
                    money=money,
                    custom_message=f"Помощь {user_url} ({processed_role.pretty_role}) "
                    f"в голосовании за {url} ({role.pretty_role})",
                    user_url=url,
                    processed_role=role,
                    at_night=False,
                )
                return
