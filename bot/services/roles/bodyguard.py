from cache.cache_types import GameCache
from services.roles.base import ActiveRoleAtNight
from cache.roleses import Groupings
from services.roles.base.mixins import TreatmentMixin
from states.states import UserFsm


class Bodyguard(TreatmentMixin, ActiveRoleAtNight):
    role = "Телохранитель"
    mail_message = "За кого пожертвовать собой?"
    photo = "https://sun6-22.userapi.com/impg/zAaADEA19scv86EFl8bY1wUYRCJyBPGg1qamiA/xjMRCUhA20g.jpg?"
    "size=1280x1280&quality=96&"
    "sign=de22e32d9a16e37a3d46a2df767eab0b&c_uniq_tag="
    "EOC9ErRHImjvmda4Qd5Pq59HPf-wUgr77rzHZvabHjc&type=album"
    grouping = Groupings.civilians
    purpose = "Тебе нужно защитить собой лучших специалистов"
    message_to_group_after_action = "Кто-то пожертвовал собой!"
    message_to_user_after_action = (
        "Ты выбрал пожертвовать собой, чтобы спасти {url}"
    )
    can_treat = True
    number_in_order_of_treatment = 3

    def __init__(self):
        self.state_for_waiting_for_action = (
            UserFsm.BODYGUARD_PROTECTS
        )

    def treat(
        self,
        game_data: GameCache,
        recovered: set[int],
        murdered: set[int],
    ):
        recovered_id = self.get_processed_user_id(game_data)
        if not recovered_id:
            return
        if recovered not in murdered:
            return
        recovered.add(recovered_id)
        if game_data[self.roles_key][0] in recovered:
            return
        murdered.add(game_data[self.roles_key][0])
