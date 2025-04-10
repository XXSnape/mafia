from abc import ABC, abstractmethod
from typing import (
    TYPE_CHECKING,
    TypedDict,
    TypeAlias,
    Unpack,
)

from cache.cache_types import (
    GameCache,
    UserIdStr,
    UserIdInt,
    PlayersIds,
)
from general import settings
from general.text import ATTEMPT_TO_KILL
from general.groupings import Groupings
from mafia.roles.base import ActiveRoleAtNightABC
from utils.informing import notify_aliases_about_transformation
from utils.pretty_text import make_pretty

if TYPE_CHECKING:
    from mafia.roles import RoleABC
from utils.roles import get_processed_user_id_if_exists, change_role

KillersOf: TypeAlias = dict[UserIdInt, list[ActiveRoleAtNightABC]]


class NightResources(TypedDict, total=True):
    recovered: PlayersIds
    murdered: PlayersIds
    victims: set[UserIdInt]
    killers_of: KillersOf


class DailyResources(TypedDict, total=True):
    is_not_there_removed: bool
    initial_removed_user_id: int | None


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
            payment = 30 * (
                len(game_data["players"])
                // settings.mafia.minimum_number_of_players
            )
            payment -= 5 * nights_lived
            if payment < 5:
                payment = 5
            return payment, 0
        return 0, 0


class ProcedureAfterNightABC(ABC):
    number_in_order_after_night: int = 1

    @abstractmethod
    async def procedure_after_night(
        self, game_data: GameCache, **kwargs: Unpack[NightResources]
    ):
        pass

    @abstractmethod
    async def accrual_of_overnight_rewards(
        self,
        game_data: GameCache,
        **kwargs: Unpack[NightResources],
    ):
        pass


class MurderAfterNightABC(ProcedureAfterNightABC):
    notification_message = ATTEMPT_TO_KILL

    @get_processed_user_id_if_exists
    async def procedure_after_night(
        self,
        murdered: PlayersIds,
        processed_user_id: UserIdInt,
        killers_of: KillersOf,
        **kwargs: Unpack[NightResources],
    ):
        killers_of[processed_user_id].append(self)
        murdered.append(processed_user_id)


class ProcedureAfterVotingABC(ABC):
    number_in_order_after_voting: int = 1

    @abstractmethod
    async def take_action_after_voting(
        self,
        game_data: GameCache,
        **kwargs: Unpack[DailyResources],
    ): ...


class FinisherOfNight(ABC):
    @abstractmethod
    async def end_night(self, game_data: GameCache): ...


class MafiaConverterABC(FinisherOfNight):
    @abstractmethod
    def check_for_possibility_to_transform(
        self, game_data: GameCache
    ) -> list["RoleABC"] | None: ...

    async def end_night(self, game_data: GameCache):
        from mafia.roles import MafiaAlias

        roles = self.check_for_possibility_to_transform(game_data)
        if not roles:
            return
        user_id = roles[0]
        if MafiaAlias.role_id not in self.all_roles:
            mafia = MafiaAlias()
            mafia(
                all_roles=self.all_roles,
                dispatcher=self.dispatcher,
                bot=self.bot,
                state=self.state,
            )
            self.all_roles[MafiaAlias.role_id] = mafia
        change_role(
            game_data=game_data,
            previous_role=self,
            new_role=MafiaAlias(),
            user_id=user_id,
        )
        await notify_aliases_about_transformation(
            game_data=game_data,
            bot=self.bot,
            new_role=MafiaAlias(),
            user_id=user_id,
        )
        await self.bot.send_photo(
            chat_id=game_data["game_chat"],
            photo=MafiaAlias.photo,
            caption=f"{make_pretty(self.role)} превращается в {make_pretty(MafiaAlias.role)}",
        )
