from cache.cache_types import GameCache
from cache.roleses import Groupings
from services.roles.base import ActiveRoleAtNight
from services.roles.base.mixins import (
    ProcedureAfterNight,
)
from states.states import UserFsm


class Bodyguard(ProcedureAfterNight, ActiveRoleAtNight):
    role = "Телохранитель"
    mail_message = "За кого пожертвовать собой?"
    photo = (
        "https://sun6-22.userapi.com/impg/zAaADEA19scv86EFl8bY1wUYRCJyBPGg1qamiA/"
        "xjMRCUhA20g.jpg?size=1280x1280&quality=96&sign="
        "de22e32d9a16e37a3d46a2df767eab0b&c_uniq_tag=EOC9ErRHImjvmda4Qd5Pq59H"
        "Pf-wUgr77rzHZvabHjc&type=album"
    )
    grouping = Groupings.civilians
    purpose = "Тебе нужно защитить собой лучших специалистов"
    message_to_group_after_action = "Кто-то пожертвовал собой!"
    message_to_user_after_action = (
        "Ты выбрал пожертвовать собой, чтобы спасти {url}"
    )
    can_treat = True
    number_in_order = 3

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

    # def treat(
    #     self,
    #     game_data: GameCache,
    #     recovered: list[int],
    #     murdered: list[int],
    # ):
    #     recovered_id = self.get_processed_user_id(game_data)
    #     if not recovered_id:
    #         return
    #     if recovered_id in recovered:
    #         return
    #     if recovered_id in murdered:
    #         recovered.append(recovered_id)
    #         if game_data[self.roles_key][0] in recovered:
    #             return
    #         murdered.append(game_data[self.roles_key][0])
