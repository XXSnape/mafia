from database.dao.base import BaseDAO
from database.models import GameModel


class GamesDao(BaseDAO[GameModel]):
    model = GameModel
