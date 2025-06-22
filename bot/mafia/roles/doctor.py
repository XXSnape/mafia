from cache.cache_types import (
    RolesLiteral,
)
from mafia.roles.base import (
    ActiveRoleAtNightABC,
    AliasRoleABC,
)
from mafia.roles.base.mixins import (
    HealerAfterNightABC,
)
from mafia.roles.descriptions.description import RoleDescription
from mafia.roles.descriptions.texts import (
    CAN_CHOOSE_YOURSELF,
    CAN_CHOOSE_YOURSELF_AFTER_2_NIGHTS,
    CANT_CHOOSE_IN_ROW,
    SAVING_PLAYER,
)


class Doctor(HealerAfterNightABC, ActiveRoleAtNightABC):
    role = "Главный врач"
    role_id: RolesLiteral = "doctor"
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
    words_to_aliases_and_teammates = "Вылечить"
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


class DoctorAlias(AliasRoleABC, Doctor):
    role = "Медсестра"
    role_id: RolesLiteral = "nurse"
    photo = "https://cdn.culture.ru/images/e2464a8d-222e-54b1-9016-86f63e902959"

    purpose = "Тебе нужно во всем помогать главврачу. В случае его смерти вступишь в должность."
    payment_for_treatment = 13
    payment_for_murder = 12
