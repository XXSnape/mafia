from cache.cache_types import GameCache, UserIdInt
from mafia.roles.descriptions.texts import (
    CANT_CHOOSE_IN_ROW,
    CAN_CHOOSE_YOURSELF,
    CAN_CHOOSE_YOURSELF_AFTER_2_NIGHTS,
)
from mafia.roles.base.mixins import ProcedureAfterVotingABC
from mafia.roles.base.roles import RoleABC
from mafia.roles.descriptions.description import RoleDescription
from general.groupings import Groupings
from mafia.roles.base import ActiveRoleAtNightABC
from states.states import UserFsm
from utils.pretty_text import make_build
from utils.roles import get_processed_role_and_user_if_exists


class Lawyer(ProcedureAfterVotingABC, ActiveRoleAtNightABC):
    role = "Адвокат"
    role_id = "lawyer"
    mail_message = "Кого защитить на голосовании?"
    is_self_selecting = True
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

    @property
    def role_description(self) -> RoleDescription:
        return RoleDescription(
            skill="Спасает игрока от повешения",
            pay_for=["Спасение игрока союзной группировки"],
            limitations=[
                CANT_CHOOSE_IN_ROW,
                CAN_CHOOSE_YOURSELF_AFTER_2_NIGHTS,
            ],
            features=[CAN_CHOOSE_YOURSELF],
        )

    @get_processed_role_and_user_if_exists
    async def take_action_after_voting(
        self,
        game_data: GameCache,
        processed_role: RoleABC,
        user_url: str,
        removed_user: list[int],
        processed_user_id: UserIdInt,
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
