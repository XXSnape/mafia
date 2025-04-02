from contextlib import suppress

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import ChatPermissions
from cache.cache_types import GameCache
from mafia.roles.base.roles import Role
from general.groupings import Groupings
from mafia.roles.base import ActiveRoleAtNight
from mafia.roles.base.mixins import (
    ProcedureAfterNight,
    ProcedureAfterVoting,
)
from states.states import UserFsm
from utils.roles import (
    get_processed_user_id_if_exists,
    get_processed_role_and_user_if_exists,
)
from utils.tg import ban_user


class Prosecutor(
    ProcedureAfterVoting, ProcedureAfterNight, ActiveRoleAtNight
):
    role = "Прокурор"
    role_id = "prosecutor"
    mail_message = "Кого арестовать этой ночью?"
    photo = (
        "https://avatars.mds.yandex.net/i?"
        "id=b5115d431dafc24be07a55a8b6343540_l-5205087-"
        "images-thumbs&n=13"
    )
    purpose = (
        "Тебе нельзя допустить, чтобы днем мафия могла говорить."
    )
    message_to_group_after_action = (
        "По данным разведки потенциальный злоумышленник арестован!"
    )
    message_to_user_after_action = "Ты выбрал арестовать {url}"
    payment_for_murder = 12

    @get_processed_user_id_if_exists
    async def procedure_after_night(
        self, game_data: GameCache, processed_user_id: int, **kwargs
    ):
        await ban_user(
            bot=self.bot,
            chat_id=game_data["game_chat"],
            user_id=processed_user_id,
        )

    @get_processed_role_and_user_if_exists
    async def accrual_of_overnight_rewards(
        self,
        game_data: GameCache,
        processed_role: Role,
        user_url: str,
        processed_user_id: int,
        **kwargs,
    ):
        money = (
            0
            if processed_role.grouping == Groupings.civilians
            else 20
        )
        self.add_money_to_all_allies(
            game_data=game_data,
            money=money,
            user_url=user_url,
            processed_role=processed_role,
            beginning_message="Арест",
        )

    @get_processed_user_id_if_exists
    async def take_action_after_voting(
        self,
        game_data: GameCache,
        processed_user_id: int,
        **kwargs,
    ):
        with suppress(TelegramBadRequest):
            await self.bot.restrict_chat_member(
                chat_id=game_data["game_chat"],
                user_id=processed_user_id,
                permissions=ChatPermissions(
                    can_send_messages=True,
                    can_send_other_messages=True,
                    can_send_polls=True,
                ),
            )

    def __init__(self):
        self.state_for_waiting_for_action = (
            UserFsm.PROSECUTOR_ARRESTS
        )
