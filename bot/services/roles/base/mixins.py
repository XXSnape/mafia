from functools import total_ordering

from cache.cache_types import GameCache
from utils.utils import make_pretty, get_profiles


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
            live_players_ids=game_data[self.roles_key],
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


class VictimsMixin:
    def get_victims(self, game_data: GameCache):
        if game_data[self.processed_users_key]:
            return set(game_data[self.processed_users_key][0])
        return set()


@total_ordering
class TreatmentMixin:
    number_in_order_of_treatment: int = 1

    def treat(
        self,
        game_data: GameCache,
        recovered: set[int],
        murdered: set[int],
    ):
        recovered_id = self.get_processed_user_id(game_data)
        if recovered_id is not None:
            recovered.add(recovered_id)

    def __eq__(self, other):
        if isinstance(other, TreatmentMixin):
            return (
                self.number_in_order_of_treatment
                == other.number_in_order_of_treatment
            )
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, TreatmentMixin):
            return (
                self.number_in_order_of_treatment
                < other.number_in_order_of_treatment
            )
        return NotImplemented
