from mafia.roles.base import RoleABC
from mafia.roles.descriptions.description import RoleDescription
from mafia.roles.descriptions.texts import PAYMENT_FOR_NIGHTS


class Hacker(RoleABC):
    role = "Белый хакер"
    role_id = "hacker"
    photo = "https://i.pinimg.com/originals/d0/e0/b5/d0e0b5198b0ea334fa243b9afd459f6b.png"
    purpose = "Ты можешь прослушивать диалоги мафии и узнавать, за кого они голосуют"
    payment_for_murder = 16
    payment_for_treatment = 15
    payment_for_night_spent = 7

    @property
    def role_description(self) -> RoleDescription:
        return RoleDescription(
            skill="Видит разговоры мафии и тех, кого они пытаются убить",
            pay_for=[PAYMENT_FOR_NIGHTS],
        )
