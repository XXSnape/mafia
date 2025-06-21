from cache.cache_types import (
    GameCache,
    PlayersIds,
    RolesLiteral,
    UserIdInt,
)
from general import settings
from general.groupings import Groupings
from mafia.roles.base import ActiveRoleAtNightABC
from mafia.roles.base.mixins import (
    KillersOf,
    ProcedureAfterNightABC,
)
from mafia.roles.base.roles import RoleABC
from mafia.roles.descriptions.description import RoleDescription
from mafia.roles.descriptions.texts import (
    CANT_CHOOSE_IN_ROW,
    SAVING_PLAYER,
)
from states.game import UserFsm
from utils.roles import get_processed_role_and_user_if_exists


class Bodyguard(ProcedureAfterNightABC, ActiveRoleAtNightABC):
    role = "Телохранитель"
    role_id: RolesLiteral = "bodyguard"
    mail_message = "За кого пожертвовать собой?"
    photo = "https://i.pinimg.com/originals/d7/27/c2/d727c2dc975bd8a14f1f947c88aeff9b.gif"
    purpose = "Тебе нужно защитить собой лучших специалистов"
    message_to_group_after_action = "Кто-то пожертвовал собой!"
    message_to_user_after_action = (
        "Ты выбрал пожертвовать собой, чтобы спасти {url}"
    )
    number_in_order_after_night = 3
    payment_for_treatment = 12
    payment_for_murder = 12

    @property
    def role_description(self) -> RoleDescription:
        return RoleDescription(
            skill="Спасает игрока от смерти ночью и умирает сам",
            pay_for=[SAVING_PLAYER],
            limitations=[
                CANT_CHOOSE_IN_ROW,
                "Выплата не происходит, если выбранного игрока лечил кто-то другой",
            ],
            features=[
                "Если вылечат телохранителя, "
                "а выбор телохранителя падёт на игрока, который должен умереть, "
                "тогда этот игрок не умрет, как и сам телохранителя, которому заплатят, как за спасение"
            ],
        )

    async def procedure_after_night(
        self,
        game_data: GameCache,
        recovered: PlayersIds,
        murdered: PlayersIds,
        killers_of: KillersOf,
        **kwargs,
    ):
        recovered_id = self.get_processed_user_id(game_data)
        if not recovered_id:
            return
        recovered.append(recovered_id)
        if (
            recovered_id in murdered
            and recovered.count(recovered_id) == 1
        ):
            saver_id = game_data[self.roles_key][0]
            murdered.append(saver_id)
            for role in killers_of[recovered_id]:
                game_data[role.processed_users_key][:] = [saver_id]
            killers_of[saver_id] = list(
                set(killers_of[saver_id])
                | set(killers_of[recovered_id])
            )
            killers_of[recovered_id] = []

    @get_processed_role_and_user_if_exists
    async def accrual_of_overnight_rewards(
        self,
        game_data: GameCache,
        recovered: PlayersIds,
        murdered: PlayersIds,
        processed_role: RoleABC,
        user_url: str,
        processed_user_id: UserIdInt,
        **kwargs,
    ):
        if (processed_user_id not in murdered) or (
            processed_user_id in murdered
            and recovered.count(processed_user_id) > 1
        ):
            return
        if processed_role.grouping != Groupings.civilians:
            money = 0
        else:
            money = (
                processed_role.payment_for_treatment
                * 5
                * (
                    len(game_data["players"])
                    // settings.mafia.minimum_number_of_players
                )
            )
        self.add_money_to_all_allies(
            game_data=game_data,
            money=money,
            beginning_message="Пожертвование собой ради",
            user_url=user_url,
            processed_role=processed_role,
        )
