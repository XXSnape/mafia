from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from cache.cache_types import GameCache, UserIdStr
from general.groupings import Groupings

from utils.roles import get_processed_user_id_if_exists


class SuicideRoleMixin:
    def __init__(self):
        self._winners = []

    def get_money_for_victory_and_nights(
        self,
        game_data: GameCache,
        nights_lived: int,
        winning_group: Groupings,
        user_id: UserIdStr,
    ):
        if int(user_id) in self._winners:
            payment = 30 * (len(game_data["players"]) // 4)
            payment -= 5 * nights_lived
            if payment < 5:
                payment = 5
            return payment, 0
        return 0, 0


class ProcedureAfterNight(ABC):
    number_in_order_after_night: int = 1

    @abstractmethod
    async def procedure_after_night(self, *args, **kwargs):
        pass

    @abstractmethod
    async def accrual_of_overnight_rewards(
        self,
        game_data: GameCache,
        **kwargs,
    ):
        pass


class MurderAfterNight(ProcedureAfterNight):

    @get_processed_user_id_if_exists
    async def procedure_after_night(
        self,
        murdered: list[int],
        processed_user_id: int,
        **kwargs,
    ):
        murdered.append(processed_user_id)


class ProcedureAfterVoting(ABC):
    number_in_order_after_voting: int = 1

    @abstractmethod
    async def take_action_after_voting(
        self,
        game_data: GameCache,
        **kwargs,
    ): ...
