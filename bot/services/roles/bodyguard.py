from cache.cache_types import GameCache
from services.roles.base.roles import Groupings, Role
from services.roles.base import ActiveRoleAtNight
from services.roles.base.mixins import (
    ProcedureAfterNight,
)
from states.states import UserFsm
from utils.validators import get_processed_role_and_user_if_exists


class Bodyguard(ProcedureAfterNight, ActiveRoleAtNight):
    role = "Телохранитель"
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
    can_treat = True
    number_in_order = 3
    payment_for_treatment = 12
    payment_for_murder = 12

    def __init__(self):
        self.state_for_waiting_for_action = (
            UserFsm.BODYGUARD_PROTECTS
        )

    async def procedure_after_night(
        self,
        game_data: GameCache,
        recovered: list[int],
        murdered: list[int],
    ):
        recovered_id = self.get_processed_user_id(game_data)
        if not recovered_id:
            return
        if recovered_id in recovered:
            return
        if recovered_id in murdered:
            recovered.append(recovered_id)
            if game_data[self.roles_key][0] in recovered:
                return
            murdered.append(game_data[self.roles_key][0])

    @get_processed_role_and_user_if_exists
    async def accrual_of_overnight_rewards(
        self,
        *,
        game_data: GameCache,
        all_roles: dict[str, Role],
        recovered: list[int],
        murdered: list[int],
        processed_role: Role,
        user_url: str,
        processed_user_id: int,
    ):
        if (processed_user_id not in murdered) or (
            processed_user_id in murdered
            and game_data[self.roles_key][0] in recovered
        ):
            return
        if processed_role.grouping != Groupings.civilians:
            money = 0
        else:
            money = processed_role.payment_for_treatment * 7
        self.add_money_to_all_allies(
            game_data=game_data,
            money=money,
            beginning_message="Пожертвование собой ради",
            user_url=user_url,
            processed_role=processed_role,
        )
