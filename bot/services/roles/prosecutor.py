from contextlib import suppress

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import ChatPermissions
from cache.cache_types import GameCache
from services.roles.base.roles import Groupings, Role
from services.roles.base import ActiveRoleAtNight
from services.roles.base.mixins import ProcedureAfterNight
from states.states import UserFsm
from utils.validators import (
    get_processed_user_id_if_exists,
    get_processed_role_and_user_if_exists,
)


class Prosecutor(ProcedureAfterNight, ActiveRoleAtNight):
    role = "Прокурор"
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
        self, game_data: GameCache, processed_user_id: int
    ):
        with suppress(TelegramBadRequest):
            await self.bot.restrict_chat_member(
                chat_id=game_data["game_chat"],
                user_id=processed_user_id,
                permissions=ChatPermissions(can_send_messages=False),
            )

    @get_processed_role_and_user_if_exists
    async def accrual_of_overnight_rewards(
        self,
        *,
        game_data: GameCache,
        all_roles: dict[str, Role],
        processed_role: Role,
        user_url: str,
        processed_user_id: int,
    ):
        money = (
            0
            if processed_role.grouping == Groupings.civilians
            else 12
        )
        for player_id in game_data[self.roles_key]:
            game_data["players"][str(player_id)]["money"] += money
            game_data["players"][str(player_id)][
                "achievements"
            ].append(
                f'Ночь {game_data["number_of_night"]}. '
                f"Арест {user_url} ({processed_role.role}) - {money}💵"
            )

    @get_processed_user_id_if_exists
    async def take_action_after_voting(
        self,
        game_data: GameCache,
        user_id: int,
        processed_user_id: int,
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
