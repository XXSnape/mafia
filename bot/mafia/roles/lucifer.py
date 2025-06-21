from contextlib import suppress
from typing import TYPE_CHECKING

from aiogram.exceptions import TelegramAPIError
from aiogram.types import InlineKeyboardButton
from cache.cache_types import GameCache, RolesLiteral, UserIdInt
from general.groupings import Groupings
from general.text import (
    NUMBER_OF_DAY,
)
from keyboards.inline.keypads.mailing import (
    send_selection_to_players_kb,
)
from mafia.roles.base import ActiveRoleAtNightABC
from mafia.roles.base.mixins import (
    ProcedureAfterNightABC,
)
from mafia.roles.descriptions.description import RoleDescription
from mafia.roles.descriptions.texts import (
    MAKES_MOVE_EVERY_ODD_NIGHT,
)
from states.game import UserFsm
from utils.common import get_criminals_ids
from utils.pretty_text import make_build
from utils.roles import get_processed_role_and_user_if_exists
from utils.tg import ban_user

if TYPE_CHECKING:
    from mafia.roles import RoleABC


class Lucifer(ProcedureAfterNightABC, ActiveRoleAtNightABC):
    role = "Люцифер"
    role_id: RolesLiteral = "lucifer"
    photo = "https://masterpiecer-images.s3.yandex.net/9bd6ec1c5b6911ee93bebeb332dff282:upscaled"
    grouping = Groupings.criminals
    need_to_monitor_interaction = False
    purpose = (
        "Каждую нечётную ночь ты забираешь душу жертвы, "
        "поэтому она не сможет ничего сделать в ночное время, а также говорить и голосовать днём."
    )
    message_to_group_after_action = (
        "Повелитель преисподней отправился в поиски невинной души"
    )
    message_to_user_after_action = (
        "Ты выбрал забрать с собой на ночь и день душу {url}"
    )
    words_to_aliases_and_teammates = "Забрать душу"
    mail_message = "Чью душу заберешь?"
    payment_for_treatment = 0
    payment_for_murder = 15
    number_in_order_after_night = -1

    @property
    def role_description(self) -> RoleDescription:
        from .sleeper import Sleeper

        return RoleDescription(
            skill="Отменяет ход жертвы ночью и запрещает говорить и голосовать ей днём",
            pay_for=["Блокировку игрока не союзной группировки"],
            limitations=[MAKES_MOVE_EVERY_ODD_NIGHT],
            features=[
                f"Усыпление Люцифера происходит раньше всех, "
                f"поэтому если он выбрал усыпить {Sleeper.pretty_role},"
                f" а она его, то будет отменен ход {Sleeper.pretty_role}"
            ],
        )

    def __init__(self):
        self.state_for_waiting_for_action = UserFsm.LUCIFER_BLOCKS

    @get_processed_role_and_user_if_exists
    async def procedure_after_night(
        self,
        game_data: GameCache,
        processed_role: "RoleABC",
        user_url: str,
        processed_user_id: UserIdInt,
        **kwargs,
    ):
        user_role = game_data["players"][str(processed_user_id)][
            "role_id"
        ]
        role: RoleABC = self.all_roles[user_role]
        if isinstance(role, ActiveRoleAtNightABC) is True:
            role.cancel_actions(
                game_data=game_data, user_id=processed_user_id
            )
        game_data["cant_talk"].append(processed_user_id)
        game_data["cant_vote"].append(processed_user_id)
        with suppress(TelegramAPIError):
            await self.bot.send_message(
                chat_id=processed_user_id,
                text=make_build(
                    NUMBER_OF_DAY.format(
                        game_data["number_of_night"]
                    )
                    + "🚫Твою душу забрали на день и ночь, "
                    "ты не можешь общаться с жителями города"
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

    def generate_markup(
        self,
        player_id: UserIdInt,
        game_data: GameCache,
    ):
        return send_selection_to_players_kb(
            players_ids=game_data["live_players_ids"],
            players=game_data["players"],
            exclude=get_criminals_ids(game_data),
        )

    @get_processed_role_and_user_if_exists
    async def accrual_of_overnight_rewards(
        self,
        game_data: GameCache,
        processed_role: "RoleABC",
        user_url: str,
        processed_user_id: UserIdInt,
        **kwargs,
    ):
        if processed_role.grouping == Groupings.criminals:
            money = 0
        else:
            money = processed_role.payment_for_murder * 2
        self.add_money_to_all_allies(
            game_data=game_data,
            money=money,
            beginning_message="Блокировка",
            user_url=user_url,
            processed_role=processed_role,
        )

    @staticmethod
    def allow_sending_mailing(game_data: GameCache):
        if game_data["number_of_night"] % 2 != 0:
            return True
        return None
