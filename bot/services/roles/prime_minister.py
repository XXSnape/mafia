from cache.roleses import Groupings
from services.roles.base import Role


class PrimeMinister(Role):
    role = "Премьер-министр"
    photo = "https://avatars.mds.yandex.net/i?id=fb2e5e825d183d5344d93bc5636bc4c4_l-5084109-images-thumbs&n=13"
    grouping = Groupings.civilians
    purpose = "Твой голос стоит как 2!"
