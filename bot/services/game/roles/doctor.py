from cache.cache_types import GameCache
from services.game.roles.base.roles import Role
from general.groupings import Groupings
from services.game.roles.base import (
    ActiveRoleAtNight,
    AliasRole,
    BossIsDeadMixin,
)
from services.game.roles.base.mixins import ProcedureAfterNight
from states.states import UserFsm
from utils.roles import (
    get_processed_user_id_if_exists,
    get_processed_role_and_user_if_exists,
)


class Doctor(
    ProcedureAfterNight, BossIsDeadMixin, ActiveRoleAtNight
):
    role = "Главный врач"
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

    @get_processed_user_id_if_exists
    async def procedure_after_night(
        self,
        game_data: GameCache,
        processed_user_id: int,
        recovered: list[int],
        **kwargs,
    ):
        recovered.append(processed_user_id)

    @get_processed_role_and_user_if_exists
    async def accrual_of_overnight_rewards(
        self,
        game_data: GameCache,
        murdered: list[int],
        processed_role: Role,
        user_url: str,
        processed_user_id: int,
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


class DoctorAlias(AliasRole, Doctor):
    role = "Медсестра"
    photo = "https://cdn.culture.ru/images/e2464a8d-222e-54b1-9016-86f63e902959"

    purpose = "Тебе нужно во всем помогать главврачу. В случае его смерти вступишь в должность."
    payment_for_treatment = 13
    payment_for_murder = 12
