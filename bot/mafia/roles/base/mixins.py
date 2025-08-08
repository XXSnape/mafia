from abc import ABC, abstractmethod
from typing import (
    TYPE_CHECKING,
    Optional,
    TypeAlias,
    TypedDict,
    Unpack,
)

from cache.cache_types import (
    GameCache,
    PlayersIds,
    RolesLiteral,
    UserIdInt,
    UserIdStr,
)
from general import settings
from general.groupings import Groupings
from general.text import ATTEMPT_TO_KILL
from utils.informing import notify_aliases_about_transformation

from mafia.roles.base import ActiveRoleAtNightABC

if TYPE_CHECKING:
    from mafia.roles import RoleABC

from utils.roles import (
    change_role,
    get_processed_role_and_user_if_exists,
    get_processed_user_id_if_exists,
)

KillersOf: TypeAlias = dict[UserIdInt, list[ActiveRoleAtNightABC]]


class NightResources(TypedDict, total=True):
    recovered: PlayersIds
    murdered: PlayersIds
    victims: set[UserIdInt]
    killers_of: KillersOf


class DailyResources(TypedDict, total=True):
    is_not_there_removed: bool
    initial_removed_user_id: int | None
    removed_user: list[int]


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
            payment = 110 * (
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


class HealerAfterNightABC(ProcedureAfterNightABC):
    coefficient: int = 1
    additional_players_attr: str | None = None

    @get_processed_user_id_if_exists
    async def procedure_after_night(
        self,
        game_data: GameCache,
        processed_user_id: UserIdInt,
        recovered: PlayersIds,
        **kwargs,
    ):
        recovered.append(processed_user_id)

    @get_processed_role_and_user_if_exists
    async def accrual_of_overnight_rewards(
        self,
        game_data: GameCache,
        murdered: PlayersIds,
        processed_role: "RoleABC",
        user_url: str,
        processed_user_id: UserIdInt,
        **kwargs,
    ):
        if processed_user_id not in murdered:
            return
        money = int(
            processed_role.payment_for_treatment * self.coefficient
        )
        additional_players = None
        if self.additional_players_attr:
            additional_players = getattr(
                self, self.additional_players_attr
            )
        self.add_money_to_all_allies(
            game_data=game_data,
            money=money,
            beginning_message="Лечение",
            user_url=user_url,
            processed_role=processed_role,
            additional_players=additional_players,
        )


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
        mafia = MafiaAlias()
        if MafiaAlias.role_id not in self.all_roles:
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
            new_role=mafia,
            user_id=user_id,
        )
        await notify_aliases_about_transformation(
            game_data=game_data,
            bot=self.bot,
            new_role=mafia,
            user_id=user_id,
        )
        if game_data["settings"]["show_roles_after_death"]:
            await self.bot.send_photo(
                chat_id=game_data["game_chat"],
                photo=mafia.photo,
                caption=f"{self.pretty_role} превращается в {mafia.pretty_role}",
            )


class SunsetKillerABC(ABC):
    number_in_order_after_sunset: int = 1

    @abstractmethod
    def kill_after_all_actions(
        self,
        game_data: GameCache,
        current_inactive_users: list[UserIdInt],
        cured_users: list[UserIdInt],
    ) -> tuple[UserIdInt, str] | None: ...


class SpecialMoneyManagerMixin:
    successful_actions: int
    final_mission: str | None = None
    divider: int | None = None
    payment_for_successful_operation: int | None = None

    def __call__(self, *args, **kwargs):
        super().__call__(*args, **kwargs)
        self.successful_actions: int = 0
        self._number_of_necessary_actions: int | None = None

    def introducing_users_to_roles(self, game_data: GameCache):
        self._number_of_necessary_actions = (
            len(game_data["live_players_ids"]) // self.divider
        )
        self.purpose = (
            f"{self.purpose}\n\n"
            "Для победы нужно "
            + self.final_mission.format(
                count=self._number_of_necessary_actions
            ).lower()
        )
        return super().introducing_users_to_roles(
            game_data=game_data
        )

    def get_money_for_victory_and_nights(
        self,
        game_data: GameCache,
        nights_lived: int,
        **kwargs,
    ):
        if (
            self.successful_actions
            >= self._number_of_necessary_actions
        ):
            payment = (
                self.payment_for_successful_operation
                * (
                    len(game_data["players"])
                    // settings.mafia.minimum_number_of_players
                )
                * self.successful_actions
            )
            return payment, 0
        return 0, self.payment_for_night_spent * nights_lived


class DeceivedRoleMixin:
    temporary_roles: dict[UserIdInt, RolesLiteral]

    def __call__(self, *args, **kwargs):
        super().__call__(*args, **kwargs)
        self.temporary_roles = dict[UserIdInt, RolesLiteral]()

    def set_temporary_role(
        self,
        user_id: UserIdInt,
        new_role: RolesLiteral,
    ):
        self.temporary_roles[user_id] = new_role

    def add_money_to_all_allies(
        self,
        game_data: GameCache,
        money: int,
        custom_message: str | None = None,
        beginning_message: str | None = None,
        user_url: str | None = None,
        processed_role: Optional["RoleABC"] = None,
        at_night: bool | None = True,
        additional_players: PlayersIds | None = None,
    ):
        if self.temporary_roles:
            if custom_message:
                msg = custom_message
            else:
                msg = f"{beginning_message} {user_url} ({processed_role.pretty_role})"
            msg += " (🚫ОБМАНУТ ВО ВРЕМЯ ИГРЫ)"
            self.temporary_roles.clear()
            return super().add_money_to_all_allies(
                game_data=game_data,
                money=0,
                custom_message=msg,
                beginning_message=beginning_message,
                user_url=user_url,
                processed_role=processed_role,
                at_night=at_night,
                additional_players=additional_players,
            )
        return super().add_money_to_all_allies(
            game_data=game_data,
            money=money,
            custom_message=custom_message,
            beginning_message=beginning_message,
            user_url=user_url,
            processed_role=processed_role,
            at_night=at_night,
            additional_players=additional_players,
        )
