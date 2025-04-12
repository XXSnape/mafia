from mafia.roles.base import RoleABC
from mafia.roles.descriptions.description import RoleDescription
from mafia.roles.descriptions.texts import PAYMENT_FOR_NIGHTS


class Civilian(RoleABC):
    role = "Мирный житель"
    role_id = "civilian"
    photo = "https://cdn.culture.ru/c/820179.jpg"
    purpose = "Тебе нужно вычислить мафию на голосовании."
    payment_for_night_spent = 12
    there_may_be_several = True

    @property
    def role_description(self) -> RoleDescription:
        return RoleDescription(
            skill=None,
            pay_for=[PAYMENT_FOR_NIGHTS],
        )
