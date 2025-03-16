from abc import ABC, abstractmethod
from functools import total_ordering
from typing import TYPE_CHECKING, Optional

from cache.cache_types import GameCache
from constants.output import MONEY_SYM

if TYPE_CHECKING:
    from services.roles.base import Role
from utils.utils import get_profiles, make_pretty
from utils.validators import get_processed_user_id_if_exists


class BossIsDeadMixin:
    async def boss_is_dead(
        self,
        current_id: int,
    ):
        game_data: GameCache = await self.state.get_data()
        url = game_data["players"][str(current_id)]["url"]
        role = game_data["players"][str(current_id)]["pretty_role"]
        enum_name = game_data["players"][str(current_id)][
            "enum_name"
        ]
        players = game_data[self.roles_key]
        if not players:
            return
        new_boss_id = players[0]
        new_boss_url = game_data["players"][str(new_boss_id)]["url"]
        game_data["players"][str(new_boss_id)]["role"] = self.role
        game_data["players"][str(new_boss_id)]["pretty_role"] = (
            make_pretty(self.role)
        )
        game_data["players"][str(new_boss_id)][
            "enum_name"
        ] = enum_name
        await self.state.set_data(game_data)
        profiles = get_profiles(
            players_ids=game_data[self.roles_key],
            players=game_data["players"],
            role=True,
        )
        for player_id in players:
            await self.bot.send_message(
                chat_id=player_id,
                text=f"Погиб {role} {url}.\n\n"
                f"Новый {role} {new_boss_url}\n\n"
                f"Текущие союзники:\n{profiles}",
            )


class ProcedureAfterNight(ABC):
    number_in_order: int = 1

    @abstractmethod
    async def procedure_after_night(self, *args, **kwargs):
        pass

    @abstractmethod
    async def accrual_of_overnight_rewards(
        self,
        *,
        game_data: GameCache,
        all_roles: dict[str, "Role"],
        **kwargs,
    ):
        pass

    def add_money_to_all_allies(
        self,
        game_data: GameCache,
        money: int,
        custom_message: str | None = None,
        beginning_message: str | None = None,
        user_url: str | None = None,
        processed_role: Optional["Role"] = None,
    ):
        for player_id in game_data[self.roles_key]:
            game_data["players"][str(player_id)]["money"] += money
            if custom_message:
                message = custom_message
            else:
                message = f"{beginning_message} {user_url} ({make_pretty(processed_role.role)}) - {money}{MONEY_SYM}"
            game_data["players"][str(player_id)][
                "achievements"
            ].append(
                f'🌃Ночь {game_data["number_of_night"]}.\n{message}'
            )


class MurderAfterNight(ProcedureAfterNight):

    @get_processed_user_id_if_exists
    async def procedure_after_night(
        self,
        game_data: GameCache,
        murdered: list[int],
        processed_user_id: int,
    ):
        murdered.append(processed_user_id)
