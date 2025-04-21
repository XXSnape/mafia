from cache.cache_types import GameCache, PlayersIds, UserIdInt
from general.groupings import Groupings
from mafia.roles.base import (
    ActiveRoleAtNightABC,
    AliasRoleABC,
)
from mafia.roles.base.mixins import ProcedureAfterNightABC
from mafia.roles.base.roles import RoleABC
from mafia.roles.descriptions.description import RoleDescription
from mafia.roles.descriptions.texts import (
    CAN_CHOOSE_YOURSELF,
    CAN_CHOOSE_YOURSELF_AFTER_2_NIGHTS,
    CANT_CHOOSE_IN_ROW,
    SAVING_PLAYER,
)
from states.game import UserFsm
from utils.roles import (
    get_processed_role_and_user_if_exists,
    get_processed_user_id_if_exists,
)


class Doctor(ProcedureAfterNightABC, ActiveRoleAtNightABC):
    role = "Главный врач"
    role_id = "doctor"
    mail_message = "Кого вылечить этой ночью?"
    is_self_selecting = True
    do_not_choose_self = 2
    photo = "https://gipermed.ru/upload/iblock/4bf/4bfa55f59ceb538bd2c8c437e8f71e5a.jpg"
    purpose = "Тебе нужно стараться лечить тех, кому нужна помощь. "
    "Только ты можешь принимать решения."
    message_to_group_after_action = (
        "Доктор спешит кому-то на помощь!"
    )
    message_to_user_after_action = "Ты выбрал вылечить {url}"
    payment_for_treatment = 15
    payment_for_murder = 18

    @property
    def role_description(self) -> RoleDescription:
        return RoleDescription(
            skill="Спасает игрока от смерти ночью",
            pay_for=[SAVING_PLAYER],
            limitations=[
                CANT_CHOOSE_IN_ROW,
                CAN_CHOOSE_YOURSELF_AFTER_2_NIGHTS,
            ],
            features=[CAN_CHOOSE_YOURSELF],
        )

    @get_processed_user_id_if_exists
    async def procedure_after_night(
        self,
        game_data: GameCache,
        processed_user_id: UserIdInt,
        recovered: PlayersIds,
        **kwargs,
    ):
        recovered.append(processed_user_id)

    @get_processed_role_and_user_if_exists
    async def accrual_of_overnight_rewards(
        self,
        game_data: GameCache,
        murdered: PlayersIds,
        processed_role: RoleABC,
        user_url: str,
        processed_user_id: UserIdInt,
        **kwargs,
    ):
        if processed_user_id not in murdered:
            return
        if processed_role.grouping != Groupings.civilians:
            money = 0
        else:
            money = processed_role.payment_for_treatment
        self.add_money_to_all_allies(
            game_data=game_data,
            money=money,
            beginning_message="Лечение",
            user_url=user_url,
            processed_role=processed_role,
        )

    def __init__(self):
        self.state_for_waiting_for_action = UserFsm.DOCTOR_TREATS


class DoctorAlias(AliasRoleABC, Doctor):
    role = "Медсестра"
    role_id = "nurse"
    photo = "https://cdn.culture.ru/images/e2464a8d-222e-54b1-9016-86f63e902959"

    purpose = "Тебе нужно во всем помогать главврачу. В случае его смерти вступишь в должность."
    payment_for_treatment = 13
    payment_for_murder = 12
