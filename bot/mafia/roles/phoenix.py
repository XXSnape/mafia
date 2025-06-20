from random import randint

from aiogram.types import InlineKeyboardButton
from cache.cache_types import (
    GameCache,
    PlayersIds,
    RolesLiteral,
    UserIdInt,
)
from general import settings
from general.groupings import Groupings
from general.text import ATTEMPT_TO_KILL, NUMBER_OF_NIGHT
from keyboards.inline.buttons.common import REFUSE_MOVE_BTN
from mafia.roles.base import ActiveRoleAtNightABC, RoleABC
from mafia.roles.base.mixins import (
    MurderAfterNightABC,
    ProcedureAfterNightABC,
    ProcedureAfterVotingABC,
)
from mafia.roles.descriptions.description import RoleDescription
from mafia.roles.descriptions.texts import (
    CAN_CHOOSE_YOURSELF,
    CANT_CHOOSE_IN_ROW,
)
from states.game import UserFsm
from utils.informing import send_a_lot_of_messages_safely
from utils.pretty_text import make_build
from utils.roles import (
    get_processed_role_and_user_if_exists,
)
from utils.tg import resending_message


class Phoenix(
    MurderAfterNightABC,
    ProcedureAfterVotingABC,
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
    notification_message = None
    payment_for_treatment = 10
    payment_for_murder = 10
    salary = 30
    is_possible_to_skip_move = True

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

    def leave_notification_message(
        self,
        game_data: GameCache,
        context_message: str | None = None,
    ):
        if self.kills:
            context_message = ATTEMPT_TO_KILL
        else:
            context_message = "Птица жизни защитила тебя от всех угроз на день и ночь"
        return super().leave_notification_message(
            game_data=game_data, context_message=context_message
        )

    def get_money_for_victory_and_nights(
        self, game_data: GameCache, nights_lived: int, **kwargs
    ):
        if not game_data[self.roles_key]:
            return 0, 0

        return (
            len(game_data["players"])
            // settings.mafia.minimum_number_of_players
            * 40,
            self.payment_for_night_spent * nights_lived,
        )

    @get_processed_role_and_user_if_exists
    async def procedure_after_night(
        self,
        game_data: GameCache,
        recovered: PlayersIds,
        processed_role: RoleABC,
        processed_user_id: UserIdInt,
        user_url: str,
        **kwargs,
    ):
        self.kills = False
        self.heals = False
        if randint(0, 1) == 1:
            await super().procedure_after_night(
                game_data=game_data, recovered=recovered, **kwargs
            )
            self.kills = True
            action = "🔫УБИТЬ"
        else:
            recovered.append(processed_user_id)
            self.heals = True
            action = "🚑СПАСТИ"

        await send_a_lot_of_messages_safely(
            bot=self.bot,
            users=game_data[self.roles_key],
            text=make_build(
                NUMBER_OF_NIGHT.format(game_data["number_of_night"])
                + f"{action}! Так распорядилась с {user_url} судьба!"
            ),
            protect_content=game_data["settings"]["protect_content"],
        )

    @get_processed_role_and_user_if_exists
    async def accrual_of_overnight_rewards(
        self,
        game_data: GameCache,
        processed_role: RoleABC,
        user_url: str,
        **kwargs,
    ):
        if self.kills:
            action = "Попытка убить"
        else:
            action = "Спасение"
        self.add_money_to_all_allies(
            game_data=game_data,
            money=self.salary,
            user_url=user_url,
            processed_role=processed_role,
            beginning_message=action,
        )

    @get_processed_role_and_user_if_exists
    async def take_action_after_voting(
        self,
        game_data: GameCache,
        user_url: str,
        removed_user: list[int],
        processed_user_id: UserIdInt,
        **kwargs,
    ):
        if self.heals and removed_user[0] == processed_user_id:
            removed_user[:] = [0]
            await resending_message(
                bot=self.bot,
                chat_id=game_data["game_chat"],
                text=make_build(
                    f"🐦‍🔥{user_url} неожиданно возродился и взлетел! "
                    f"Жители окстились и убежали."
                ),
            )
