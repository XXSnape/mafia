from cache.cache_types import GameCache
from services.roles.base.roles import Groupings
from services.roles import Bodyguard
from services.roles.base import Role
from services.roles.base.mixins import ProcedureAfterNight


class Punisher(ProcedureAfterNight, Role):
    role = "Каратель"
    photo = "https://lastfm.freetls.fastly.net/i/u/ar0/d04cdfdf3f65412bc1e7870ec6599ed7.png"
    purpose = "Спровоцируй мафию и забери её с собой!"
    number_in_order = 4
    payment_for_treatment = 0
    payment_for_murder = 0

    async def procedure_after_night(
        self,
        game_data: GameCache,
        all_roles: dict[str, Role],  # TODO all roles
        victims: set[int],
        recovered: list[int],
        murdered: list[int],
    ):
        punishers = game_data.get(self.roles_key)
        if not punishers:
            return
        punisher_id = punishers[0]
        killed_py_punisher = set()

        if punisher_id not in set(murdered) - set(recovered):
            return
        for role in all_roles:
            current_role = all_roles[role]
            if current_role.can_kill_at_night is False:
                continue
            killed_id = current_role.get_processed_user_id(game_data)
            if not killed_id:
                continue
            killer_id = game_data[current_role.roles_key][0]
            if killed_id == punisher_id:
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
                    if current_role.grouping != Groupings.civilians:
                        money = 26
                    else:
                        money = 0
                    url = game_data["players"][str(killer_id)]["url"]
                    role = game_data["players"][str(killer_id)][
                        "role"
                    ]
                    for punisher_id in game_data[self.roles_key]:
                        game_data["players"][str(punisher_id)][
                            "money"
                        ] += money
                        game_data["players"][str(punisher_id)][
                            "achievements"
                        ].append(
                            f'Ночь {game_data["number_of_night"]}. '
                            f"Убийство {url} ({role}) - {money}💵"
                        )
        game_data["messages_after_night"].append(
            [
                punisher_id,
                "Все нарушители твоего покоя будут наказаны!",
            ]
        )
        victims |= killed_py_punisher

    # async def change_victims(
    #     self,
    #     game_data: GameCache,
    #     attacking_roles: list[Role],
    #     victims: set[int],
    #     recovered: list[int],
    # ):
    #     punishers = game_data.get(self.roles_key)
    #     if not punishers:
    #         return
    #     punisher_id = punishers[0]
    #     killed_py_punisher = set()
    #     if punisher_id not in victims:
    #         return
    #     for role in attacking_roles:
    #         killed_id = role.get_processed_user_id(game_data)
    #         if not killed_id:
    #             continue
    #         killer_id = game_data[role.roles_key][0]
    #         if killed_id == punisher_id:
    #             treated_by_bodyguard = (
    #                 Bodyguard().get_processed_user_id(game_data)
    #             )
    #             if (
    #                 treated_by_bodyguard == killer_id
    #                 and recovered.count(killer_id) == 1
    #             ):
    #                 killed_py_punisher.add(
    #                     game_data[Bodyguard.roles_key][0]
    #                 )
    #             if killer_id not in recovered:
    #                 killed_py_punisher.add(killer_id)
    #
    #     await self.bot.send_message(
    #         chat_id=punisher_id,
    #         text="Все нарушители твоего покоя будут наказаны!",
    #     )
    #     victims |= killed_py_punisher
