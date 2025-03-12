from services.roles.base.roles import Groupings


class GameIsOver(Exception):
    def __init__(self, winner: Groupings) -> None:
        super().__init__(winner)
        self.winner = winner
