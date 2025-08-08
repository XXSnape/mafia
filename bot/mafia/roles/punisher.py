from cache.cache_types import (
    GameCache,
    PlayersIds,
    RolesLiteral,
    UserIdInt,
)
from general import settings
from general.groupings import Groupings

from mafia.roles import Bodyguard
from mafia.roles.base import RoleABC
from mafia.roles.base.mixins import KillersOf, ProcedureAfterNightABC
from mafia.roles.descriptions.description import RoleDescription
from mafia.roles.descriptions.texts import (
    KILLING_PLAYER,
)


class Punisher(ProcedureAfterNightABC, RoleABC):
    role = "Каратель"
    role_id: RolesLiteral = "punisher"
    photo = "https://lastfm.freetls.fastly.net/i/u/ar0/d04cdfdf3f65412bc1e7870ec6599ed7.png"
    purpose = "Спровоцируй мафию и забери её с собой!"
    number_in_order_after_night = 4
    payment_for_treatment = 0
    payment_for_murder = 10

    @property
    def role_description(self) -> RoleDescription:
        return RoleDescription(
            skill="Если умирает ночью, забирает убийцу с собой",
            pay_for=[KILLING_PLAYER],
            features=[
                "Умирает главарь ролей, а не его союзники. "
                "Например, умрёт дон, а не мафия, даже если сам дон никого не выбрал"
            ],
        )

    def __init__(self):
        self.killed = []

    async def procedure_after_night(
        self,
        game_data: GameCache,
        recovered: PlayersIds,
        murdered: PlayersIds,
        killers_of: KillersOf,
        **kwargs
    ):
        punishers = game_data.get(self.roles_key)
        if not punishers:
            return
        punisher_id = punishers[0]
        killed_py_punisher = set()
        if punisher_id not in set(murdered) - set(recovered):
            return
        for current_role in killers_of[punisher_id]:
            killers = game_data[current_role.roles_key]
            if not killers:
                continue
            killer_id = killers[0]
            bodyguard: Bodyguard | None = self.all_roles.get(
                Bodyguard.role_id, None
            )
            treated_by_bodyguard = None
            if bodyguard:
                treated_by_bodyguard = (
                    Bodyguard().get_processed_user_id(game_data)
                )

            killed_py_punisher.add(killer_id)
            self.killed.append([killer_id, current_role])
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
                        Bodyguard(),
                    ]
                )
        game_data["messages_after_night"].append(
            [
                punisher_id,
                "Ты накажешь нарушителей своего покоя!",
            ]
        )
        for user_id in killed_py_punisher:
            killers_of[user_id].append(self)
        murdered.extend(list(killed_py_punisher))

    async def accrual_of_overnight_rewards(
        self, game_data: GameCache, victims: set[UserIdInt], **kwargs
    ):
        if not self.killed:
            return
        for killer_id, current_role in self.killed:
            if killer_id in victims:
                if current_role.grouping != Groupings.civilians:
                    money = (
                        current_role.payment_for_murder
                        * 2
                        * (
                            len(game_data["players"])
                            // settings.mafia.minimum_number_of_players
                        )
                    )
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
