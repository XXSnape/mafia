from cache.cache_types import GameCache
from cache.roleses import Groupings
from services.roles import Bodyguard
from services.roles.base import Role


class Punisher(Role):
    role = "Каратель"
    photo = "https://lastfm.freetls.fastly.net/i/u/ar0/d04cdfdf3f65412bc1e7870ec6599ed7.png"
    grouping = Groupings.civilians
    purpose = "Спровоцируй мафию и забери её с собой!"

    async def change_victims(
        self,
        game_data: GameCache,
        attacking_roles: list[Role],
        victims: set[int],
        recovered: list[int],
    ):
        punishers = game_data.get(self.roles_key)
        if not punishers:
            return
        punisher_id = punishers[0]
        killed_py_punisher = set()
        if punisher_id not in victims:
            return
        for role in attacking_roles:
            killed_id = role.get_processed_user_id(game_data)
            if not killed_id:
                continue
            killer_id = game_data[role.roles_key][0]
            if killer_id == punisher_id:
                treated_by_bodyguard = (
                    Bodyguard().get_processed_user_id(game_data)
                )
                if (
                    treated_by_bodyguard == killer_id
                    and recovered.count(killer_id) == 1
                ):
                    killed_py_punisher.add(
                        game_data[Bodyguard.roles_key][0]
                    )
                if killer_id not in recovered:
                    killed_py_punisher.add(killer_id)

        await self.bot.send_message(
            chat_id=punisher_id,
            text="Все нарушители твоего покоя будут наказаны!",
        )
        victims |= killed_py_punisher
