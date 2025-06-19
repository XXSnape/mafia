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
    CANT_CHOOSE_IN_ROW,
)
from states.game import UserFsm
from utils.roles import (
    get_processed_user_id_if_exists,
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

    def __init__(self):
        self.state_for_waiting_for_action = (
            UserFsm.MANAGER_GIVES_RIGHTS
        )

    @get_processed_user_id_if_exists
    async def take_action_after_voting(
        self,
        game_data: GameCache,
        removed_user: list[int],
        processed_user_id: UserIdInt,
        **kwargs,
    ):
        pass
