from cache.cache_types import GameCache
from services.roles.base.roles import Groupings
from services.roles import Bodyguard
from services.roles.base import Role
from services.roles.base.mixins import ProcedureAfterNight


class Punisher(ProcedureAfterNight, Role):
    role = "Каратель"
    photo = "https://lastfm.freetls.fastly.net/i/u/ar0/d04cdfdf3f65412bc1e7870ec6599ed7.png"
    purpose = "Спровоцируй мафию и забери её с собой!"
    number_in_order_after_night = 4
    payment_for_treatment = 0
    payment_for_murder = 0
    payment_for_night_spent = 8

    def __init__(self):
        self.killed = []

    async def procedure_after_night(
        self,
        game_data: GameCache,
        all_roles: dict[str, Role],  # TODO all roles
        victims: set[int],
        recovered: list[int],
        murdered: list[int],
        **kwargs
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
            if isinstance(killed_id, list):
                if punisher_id not in killed_id:
                    continue
            elif killed_id != punisher_id:
                continue
            treated_by_bodyguard = Bodyguard().get_processed_user_id(
                game_data
            )
            if (
                treated_by_bodyguard == killer_id
                and recovered.count(killer_id) == 1
            ):
                killed_py_punisher.add(
                    game_data[Bodyguard.roles_key][0]
                )
                self.killed.append(
                    [
                        game_data[Bodyguard.roles_key][0],
                        current_role,
                    ]
                )
            else:
                killed_py_punisher.add(killer_id)
                self.killed.append([killer_id, current_role])

        game_data["messages_after_night"].append(
            [
                punisher_id,
                "Все нарушители твоего покоя будут наказаны!",
            ]
        )
        murdered.extend(list(killed_py_punisher))

    async def accrual_of_overnight_rewards(
        self, game_data: GameCache, victims: set[int], **kwargs
    ):
        if not self.killed:
            return
        for killer_id, current_role in self.killed:
            if killer_id in victims:
                if current_role.grouping != Groupings.civilians:
                    money = current_role.payment_for_murder * 2
                else:
                    money = 0
                self.add_money_to_all_allies(
                    game_data=game_data,
                    money=money,
                    user_url=game_data["players"][str(killer_id)][
                        "url"
                    ],
                    processed_role=current_role,
                    beginning_message="Убийство",
                )
        self.killed.clear()
        #
        # punishers = game_data[self.roles_key]
        # if not punishers:
        #     return
        # punisher_id = punishers[0]
        # if punisher_id not in victims:
        #     return
        # for role in all_roles:
        #     current_role = all_roles[role]
        #     if current_role.can_kill_at_night is False:
        #         continue
        #     killed_id = current_role.get_processed_user_id(game_data)
        #     if isinstance(killed_id, list):
        #         if punisher_id not in killed_id:
        #             continue
        #     else:
        #         if killed_id != punisher_id:
        #             continue
        #     killer_id = game_data[current_role.roles_key][0]
        #     if killer_id in victims:
        #         if current_role.grouping != Groupings.civilians:
        #             money = current_role.payment_for_murder * 2
        #         else:
        #             money = 0
        #         self.add_money_to_all_allies(
        #             game_data=game_data,
        #             money=money,
        #             user_url=game_data["players"][str(killer_id)][
        #                 "url"
        #             ],
        #             processed_role=current_role,
        #             beginning_message="Убийство",
        #         )
