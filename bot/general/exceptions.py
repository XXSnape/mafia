from general.groupings import Groupings


class GameIsOver(Exception):
    def __init__(self, winner: Groupings) -> None:
        super().__init__(winner)
        self.winner = winner


class ActionPerformed(Exception):
    pass


class NotEnoughMoney(Exception):
    def __init__(self, balance: int):
        super().__init__(balance)
        self.balance = balance
