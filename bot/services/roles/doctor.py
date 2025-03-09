from services.roles.base import (
    AliasRole,
    BossIsDeadMixin,
    ActiveRoleAtNight,
)
from cache.roleses import Groupings
from services.roles.base.mixins import TreatmentMixin
from states.states import UserFsm


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


class Doctor(TreatmentMixin, BossIsDeadMixin, ActiveRoleAtNight):
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

    def __init__(self):
        self.state_for_waiting_for_action = UserFsm.DOCTOR_TREATS

    # alias = Alias(role=AliasesRole.nurse)
