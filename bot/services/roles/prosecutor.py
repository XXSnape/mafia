from contextlib import suppress

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import ChatPermissions

from cache.cache_types import GameCache
from services.roles.base import ActiveRoleAtNight
from cache.roleses import Groupings
from states.states import UserFsm


class Prosecutor(ActiveRoleAtNight):
    role = "Прокурор"
    mail_message = "Кого арестовать этой ночью?"
    photo = "https://avatars.mds.yandex.net/i?"
    "id=b5115d431dafc24be07a55a8b6343540_l-5205087-images-thumbs&n=13"
    grouping = Groupings.civilians
    purpose = (
        "Тебе нельзя допустить, чтобы днем мафия могла говорить."
    )
    message_to_group_after_action = (
        "По данным разведки потенциальный злоумышленник арестован!"
    )
    message_to_user_after_action = "Ты выбрал арестовать {url}"

    async def take_action_after_voting(
        self, game_data: GameCache, user_id: int
    ):
        cant_vote_id = self.get_processed_user_id(game_data)
        if cant_vote_id:
            with suppress(TelegramBadRequest):
                await self.bot.restrict_chat_member(
                    chat_id=game_data["game_chat"],
                    user_id=cant_vote_id,
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
