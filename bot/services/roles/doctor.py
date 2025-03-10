from cache.cache_types import GameCache
from cache.roleses import Groupings
from services.roles.base import (
    ActiveRoleAtNight,
    AliasRole,
    BossIsDeadMixin,
)
from services.roles.base.mixins import ProcedureAfterNight
from states.states import UserFsm
from utils.validators import get_processed_user_id_if_exists


class DoctorAlias(AliasRole):
    role = "Медсестра"
    photo = "https://cdn.culture.ru/images/e2464a8d-222e-54b1-9016-86f63e902959"

    purpose = "Тебе нужно во всем помогать главврачу. В случае его смерти вступишь в должность."

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
    can_treat = True
    do_not_choose_self = 2
    photo = "https://gipermed.ru/upload/iblock/4bf/4bfa55f59ceb538bd2c8c437e8f71e5a.jpg"
    grouping = Groupings.civilians
    purpose = "Тебе нужно стараться лечить тех, кому нужна помощь. "
    "Только ты можешь принимать решения."
    message_to_group_after_action = (
        "Доктор спешит кому-то на помощь!"
    )
    message_to_user_after_action = "Ты выбрал вылечить {url}"
    alias = DoctorAlias()
    number_in_order = 4

    @get_processed_user_id_if_exists
    async def procedure_after_night(
        self,
        game_data: GameCache,
        processed_user_id: int,
        recovered: list[int],
    ):
        recovered.append(processed_user_id)

    def __init__(self):
        self.state_for_waiting_for_action = UserFsm.DOCTOR_TREATS

    # alias = Alias(role=AliasesRole.nurse)
