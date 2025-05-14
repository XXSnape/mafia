from contextlib import suppress

from aiogram.exceptions import TelegramAPIError
from cache.cache_types import (
    GameCache,
    RolesLiteral,
    UserIdInt,
)
from general.groupings import Groupings
from general.text import NUMBER_OF_DAY
from mafia.roles.base import ActiveRoleAtNightABC
from mafia.roles.base.mixins import (
    ProcedureAfterNightABC,
)
from mafia.roles.base.roles import RoleABC
from mafia.roles.descriptions.description import RoleDescription
from mafia.roles.descriptions.texts import CANT_CHOOSE_IN_ROW
from states.game import UserFsm
from utils.pretty_text import make_build
from utils.roles import (
    get_processed_role_and_user_if_exists,
    get_processed_user_id_if_exists,
)
from utils.tg import ban_user


class Prosecutor(
    ProcedureAfterNightABC,
    ActiveRoleAtNightABC,
):
    role = "Прокурор"
    role_id: RolesLiteral = "prosecutor"
    mail_message = "Кого арестовать этой ночью?"
    photo = (
        "https://avatars.mds.yandex.net/i?"
        "id=b5115d431dafc24be07a55a8b6343540_l-5205087-"
        "images-thumbs&n=13"
    )
    purpose = "Тебе нельзя допустить, чтобы днём мафия или иные изверги могли говорить и голосовать."
    message_to_group_after_action = (
        "По данным разведки потенциальный злоумышленник арестован!"
    )
    message_to_user_after_action = "Ты выбрал арестовать {url}"
    payment_for_murder = 12

    @property
    def role_description(self) -> RoleDescription:
        return RoleDescription(
            skill="Жертва не сможет говорить днём, голосовать и подтверждать убийство",
            pay_for=["Арест игрока не союзной группировки"],
            limitations=[CANT_CHOOSE_IN_ROW],
        )

    @get_processed_user_id_if_exists
    async def procedure_after_night(
        self,
        game_data: GameCache,
        processed_user_id: UserIdInt,
        **kwargs,
    ):
        game_data["cant_talk"].append(processed_user_id)
        game_data["cant_vote"].append(processed_user_id)
        with suppress(TelegramAPIError):
            await self.bot.send_message(
                chat_id=processed_user_id,
                text=make_build(
                    NUMBER_OF_DAY.format(
                        game_data["number_of_night"]
                    )
                    + "🚫Тебе запретили общаться и принимать участие в выборах на 1 день"
                ),
                protect_content=game_data["settings"][
                    "protect_content"
                ],
            )
        await ban_user(
            bot=self.bot,
            chat_id=game_data["game_chat"],
            user_id=processed_user_id,
        )

    @get_processed_role_and_user_if_exists
    async def accrual_of_overnight_rewards(
        self,
        game_data: GameCache,
        processed_role: RoleABC,
        user_url: str,
        processed_user_id: UserIdInt,
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

    def __init__(self):
        self.state_for_waiting_for_action = (
            UserFsm.PROSECUTOR_ARRESTS
        )
