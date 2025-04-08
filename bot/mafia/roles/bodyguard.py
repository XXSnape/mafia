from cache.cache_types import GameCache, UserIdInt
from mafia.roles.descriptions.texts import (
    CANT_CHOOSE_IN_ROW,
    SAVING_PLAYER,
)
from mafia.roles.base.roles import RoleABC
from mafia.roles.descriptions.description import RoleDescription
from general.groupings import Groupings
from mafia.roles.base import ActiveRoleAtNightABC
from mafia.roles.base.mixins import (
    ProcedureAfterNightABC,
)
from states.states import UserFsm
from utils.roles import get_processed_role_and_user_if_exists


class Bodyguard(ProcedureAfterNightABC, ActiveRoleAtNightABC):
    role = "Телохранитель"
    role_id = "bodyguard"
    mail_message = "За кого пожертвовать собой?"
    photo = (
        "https://sun6-22.userapi.com/impg/zAaADEA19scv86EFl8bY1wUYRCJyBPGg1qamiA/"
        "xjMRCUhA20g.jpg?size=1280x1280&quality=96&sign="
        "de22e32d9a16e37a3d46a2df767eab0b&c_uniq_tag=EOC9ErRHImjvmda4Qd5Pq59H"
        "Pf-wUgr77rzHZvabHjc&type=album"
    )
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
            skill="Спасает игрока от смерти и умирает сам",
            pay_for=[SAVING_PLAYER],
            limitations=[
                CANT_CHOOSE_IN_ROW,
                "выплата не происходит, если выбранного игрока лечил кто-то другой",
            ],
            features=[
                "Если вылечат представителя роли, "
                "а выбор представителя роли падет на игрока, который должен умереть, "
                "тогда этот игрок не умрет, как и сам представитель роли, которому заплатят, как за спасение"
            ],
        )

    def __init__(self):
        self.state_for_waiting_for_action = (
            UserFsm.BODYGUARD_PROTECTS
        )

    async def procedure_after_night(
        self,
        game_data: GameCache,
        recovered: list[int],
        murdered: list[int],
        killers_of: dict[UserIdInt, list[ActiveRoleAtNightABC]],
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
        recovered: list[int],
        murdered: list[int],
        processed_role: RoleABC,
        user_url: str,
        processed_user_id: int,
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
                * (len(game_data["players"]) // 4)
            )
        self.add_money_to_all_allies(
            game_data=game_data,
            money=money,
            beginning_message="Пожертвование собой ради",
            user_url=user_url,
            processed_role=processed_role,
        )
