from cache.cache_types import GameCache
from mafia.roles.base.mixins import ProcedureAfterVoting
from mafia.roles.base.roles import Role
from general.groupings import Groupings
from mafia.roles.base import ActiveRoleAtNight
from states.states import UserFsm
from utils.pretty_text import make_build
from utils.roles import get_processed_role_and_user_if_exists


class Lawyer(ProcedureAfterVoting, ActiveRoleAtNight):
    role = "Адвокат"
    role_id = "lawyer"
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
    number_in_order_after_voting = 0

    @get_processed_role_and_user_if_exists
    async def take_action_after_voting(
        self,
        game_data: GameCache,
        processed_role: Role,
        user_url: str,
        removed_user: list[int],
        processed_user_id: int,
        **kwargs,
    ):
        if removed_user[0] != processed_user_id:
            return
        removed_user[:] = [0]
        if processed_role.grouping == Groupings.civilians:
            money = processed_role.payment_for_treatment * 2
        else:
            money = 0

        await self.bot.send_message(
            chat_id=game_data["game_chat"],
            text=make_build(
                f"😯У {user_url} есть алиби, поэтому местные жители отпустили гвоздя программы"
            ),
        )
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
