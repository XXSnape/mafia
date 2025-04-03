from abc import ABC, abstractmethod

from cache.cache_types import GameCache, UserIdStr, UserIdInt
from general.text import ATTEMPT_TO_KILL
from general.groupings import Groupings
from mafia.roles.base import ActiveRoleAtNight

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
    notification_message = ATTEMPT_TO_KILL

    @get_processed_user_id_if_exists
    async def procedure_after_night(
        self,
        murdered: list[int],
        processed_user_id: UserIdInt,
        killers_of: dict[UserIdInt, list[ActiveRoleAtNight]],
        **kwargs,
    ):
        killers_of[processed_user_id].append(self)
        murdered.append(processed_user_id)


class ProcedureAfterVoting(ABC):
    number_in_order_after_voting: int = 1

    @abstractmethod
    async def take_action_after_voting(
        self,
        game_data: GameCache,
        **kwargs,
    ): ...
