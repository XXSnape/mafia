from services.roles.base.roles import Groupings
from services.roles.base import Role


class PrimeMinister(Role):
    role = "Премьер-министр"
    photo = (
        "https://avatars.mds.yandex.net/i?id=fb2e5e825d183d5344d93bc563"
        "6bc4c4_l-5084109-images-thumbs&n=13"
    )
    purpose = "Твой голос стоит как 2!"
    payment_for_treatment = 12
    payment_for_murder = 12
