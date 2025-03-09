from cache.roleses import Groupings
from services.roles.base import Role


class Civilian(Role):
    role = "Мирный житель"
    photo = "https://cdn.culture.ru/c/820179.jpg"
    grouping = Groupings.civilians
    purpose = "Тебе нужно вычислить мафию на голосовании."
