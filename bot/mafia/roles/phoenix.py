from contextlib import suppress

from aiogram.exceptions import TelegramAPIError
from aiogram.types import InlineKeyboardButton

from cache.cache_types import GameCache, RolesLiteral, UserIdInt
from cache.extra import ExtraCache
from general.groupings import Groupings
from keyboards.inline.buttons.common import REFUSE_MOVE_BTN
from mafia.roles.base import ActiveRoleAtNightABC, RoleABC
from mafia.roles.base.mixins import ProcedureAfterNightABC
from mafia.roles.descriptions.description import RoleDescription
from mafia.roles.descriptions.texts import (
    CANT_CHOOSE_IN_ROW,
    CAN_CHOOSE_YOURSELF,
)
from states.game import UserFsm
from utils.pretty_text import make_build
from utils.roles import (
    get_processed_role_and_user_if_exists,
    get_processed_user_id_if_exists,
)


class Phoenix(
    ProcedureAfterNightABC,
    ActiveRoleAtNightABC,
):
    role = "Феникс"
    role_id: RolesLiteral = "phoenix"
    mail_message = "Кого случайным образом спасти или убить?"
    photo = "https://masterpiecer-images.s3.yandex.net/49fc1766571c11ee844186fcb22e0c5e:upscaled"
    grouping = Groupings.other
    purpose = "Ты случайным образом спасаешь от смерти ночью и днём или убиваешь с вероятностью 50 на 50"
    is_self_selecting = True
    message_to_group_after_action = None
    message_to_user_after_action = "Ты выбрал убить или спасти {url}"
    payment_for_treatment = 10
    payment_for_murder = 10

    @property
    def role_description(self) -> RoleDescription:

        return RoleDescription(
            skill="С одинаковой вероятностью спасает игрока от смерти ночью и на голосовании или убивает",
            pay_for=["Любое действие ночью"],
            limitations=[
                CANT_CHOOSE_IN_ROW,
            ],
            features=[
                CAN_CHOOSE_YOURSELF,
            ],
            wins_if="Выживет по итогу игры",
        )

    def __init__(self):
        self.state_for_waiting_for_action = (
            UserFsm.PHOENIX_RANDOMLY_ACTS
        )
        self.kills: bool = False
        self.heals: bool = False

    def generate_markup(
        self,
        player_id: UserIdInt,
        game_data: GameCache,
        extra_buttons: tuple[InlineKeyboardButton, ...] = (),
    ):
        extra_buttons = (REFUSE_MOVE_BTN,)
        return super().generate_markup(
            player_id=player_id,
            game_data=game_data,
            extra_buttons=extra_buttons,
        )

    @get_processed_user_id_if_exists
    async def procedure_after_night(
        self,
        game_data: GameCache,
        processed_user_id: UserIdInt,
        **kwargs,
    ):
        pass


    @get_processed_role_and_user_if_exists
    async def accrual_of_overnight_rewards(
        self,
        game_data: GameCache,
        processed_role: RoleABC,
        user_url: str,
        processed_user_id: UserIdInt,
        **kwargs,
    ):
        pass

