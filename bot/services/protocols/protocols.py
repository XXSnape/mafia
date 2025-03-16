from typing import Protocol, runtime_checkable

from cache.cache_types import GameCache
from services.roles.base import Role


@runtime_checkable
class EarliestActionsAfterNight(Protocol):
    async def earliest_actions_after_night(
        self, all_roles: dict[str, Role]
    ): ...


@runtime_checkable
class DelayedMessagesAfterNight(Protocol):
    async def send_delayed_messages_after_night(
        self, game_data: GameCache
    ): ...


@runtime_checkable
class ModificationVictims(Protocol):
    async def change_victims(
        self,
        game_data: GameCache,
        attacking_roles: list[Role],
        victims: set[int],
        recovered: list[int],
    ): ...


@runtime_checkable
class VictimsOfVote(Protocol):
    async def take_action_after_voting(
        self,
        game_data: GameCache,
        user_id: int,
        all_roles: dict[str, Role],
    ): ...


@runtime_checkable
class AchievementCalculator(Protocol):
    # @abstractmethod
    async def accrual_of_overnight_rewards(
        self,
        *,
        game_data: GameCache,
        all_roles: dict[str, "Role"],
        **kwargs,
    ): ...


# @runtime_checkable
# class AfterDeaths(Protocol):
#     async def
