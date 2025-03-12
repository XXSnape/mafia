from cache.cache_types import GameCache
from services.roles.base.roles import Groupings, Role
from services.roles.base import (
    ActiveRoleAtNight,
    AliasRole,
    BossIsDeadMixin,
)
from services.roles.base.mixins import ProcedureAfterNight
from states.states import UserFsm
from utils.validators import (
    get_processed_user_id_if_exists,
    get_processed_role_and_user_if_exists,
)


class DoctorAlias(AliasRole):
    role = "Медсестра"
    photo = "https://cdn.culture.ru/images/e2464a8d-222e-54b1-9016-86f63e902959"

    purpose = "Тебе нужно во всем помогать главврачу. В случае его смерти вступишь в должность."
    payment_for_treatment = 13
    payment_for_murder = 12

    def __init__(self):
        self.state_for_waiting_for_action = UserFsm.DOCTOR_TREATS

    @classmethod
    @property
    def roles_key(cls):
        return Doctor.roles_key

    @classmethod
    @property
    def processed_users_key(cls):
        return Doctor.processed_users_key

    @classmethod
    @property
    def last_interactive_key(cls):
        return Doctor.last_interactive_key


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
    alias = DoctorAlias()
    payment_for_treatment = 15
    payment_for_murder = 18

    @get_processed_user_id_if_exists
    async def procedure_after_night(
        self,
        game_data: GameCache,
        processed_user_id: int,
        recovered: list[int],
    ):
        recovered.append(processed_user_id)

    @get_processed_role_and_user_if_exists
    async def accrual_of_overnight_rewards(
        self,
        *,
        game_data: GameCache,
        all_roles: dict[str, Role],
        murdered: list[int],
        processed_role: Role,
        user_url: str,
        processed_user_id: int,
    ):
        if processed_user_id not in murdered:
            return
        for doctor_id in game_data[self.roles_key]:
            game_data["players"][str(doctor_id)][
                "money"
            ] += processed_role.payment_for_treatment
            game_data["players"][str(doctor_id)][
                "achievements"
            ].append(
                f'Ночь {game_data["number_of_night"]}. '
                f"Лечение {user_url} ({processed_role.role}) - {processed_role.payment_for_treatment}💵"
            )

    def __init__(self):
        self.state_for_waiting_for_action = UserFsm.DOCTOR_TREATS

    # alias = Alias(role=AliasesRole.nurse)
