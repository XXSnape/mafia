from services.roles.base.roles import Groupings
from services.roles.base import Role


class Hacker(Role):
    role = "Белый хакер"
    photo = "https://i.pinimg.com/originals/d0/e0/b5/d0e0b5198b0ea334fa243b9afd459f6b.png"
    purpose = "Ты можешь прослушивать диалоги мафии и узнавать, за кого они голосуют"
    payment_for_murder = 16
    payment_for_treatment = 15
