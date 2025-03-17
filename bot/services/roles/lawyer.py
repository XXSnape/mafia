from cache.cache_types import GameCache
from services.roles.base.roles import Groupings, Role
from services.roles.base import ActiveRoleAtNight
from states.states import UserFsm
from utils.validators import get_processed_role_and_user_if_exists


class Lawyer(ActiveRoleAtNight):
    role = "Адвокат"
    mail_message = "Кого защитить на голосовании?"
    do_not_choose_self = 2
    photo = (
        "https://avatars.mds.yandex.net/get-altay/"
        "5579175/2a0000017e0aa51c3c1fd887206b0156ee34/XXL_height"
    )
    purpose = "Тебе нужно защитить мирных жителей от своих же на голосовании."
    message_to_group_after_action = (
        "Кому-то обеспечена защита лучшими адвокатами города!"
    )
    message_to_user_after_action = "Ты выбрал защитить {url}"

    @get_processed_role_and_user_if_exists
    async def take_action_after_voting(
        self,
        game_data: GameCache,
        processed_role: Role,
        user_url: str,
        protected_user_id: int | None = None,
        **kwargs,
    ):
        if protected_user_id is None:
            return
        if processed_role.grouping == Groupings.civilians:
            money = int(processed_role.payment_for_treatment * 1.5)
        else:
            money = 0
        self.add_money_to_all_allies(
            game_data=game_data,
            money=money,
            beginning_message="Защита",
            user_url=user_url,
            processed_role=processed_role,
            at_night=False,
        )

    def __init__(self):
        self.state_for_waiting_for_action = UserFsm.LAWYER_PROTECTS
