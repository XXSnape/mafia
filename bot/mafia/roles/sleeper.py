from contextlib import suppress

from aiogram.exceptions import TelegramAPIError
from cache.cache_types import GameCache, RolesLiteral, UserIdInt
from cache.extra import ExtraCache
from general.groupings import Groupings
from mafia.roles.base import ActiveRoleAtNightABC, RoleABC
from mafia.roles.base.mixins import ProcedureAfterNightABC
from mafia.roles.descriptions.description import RoleDescription
from mafia.roles.descriptions.texts import CANT_CHOOSE_IN_ROW
from utils.pretty_text import make_build
from utils.roles import (
    get_processed_role_and_user_if_exists,
    get_processed_user_id_if_exists,
)


class Sleeper(ProcedureAfterNightABC, ActiveRoleAtNightABC):
    role = "Клофелинщица"
    role_id: RolesLiteral = "sleeper"
    mail_message = "Кого усыпить этой ночью?"
    photo = (
        "https://masterpiecer-images.s3.yandex.net/c94e9c"
        "b6787b11eeb1ce1e5d9776cfa6:upscaled"
    )
    grouping = Groupings.civilians
    purpose = (
        "Ты можешь усыпить кого-нибудь и не дать сделать ход ночью"
    )
    message_to_group_after_action = "Спят взрослые и дети. Не обошлось и без помощи клофелинщиков!"
    message_to_user_after_action = "Ты выбрал усыпить {url}"
    extra_data = [
        ExtraCache(key="tracking", data_type=dict),
    ]
    number_in_order_after_night = 0
    payment_for_treatment = 8
    payment_for_murder = 8

    @property
    def role_description(self) -> RoleDescription:
        from .angel import Angel
        from .mafia import Mafia

        return RoleDescription(
            skill="Отменяет ночные ходы жертвы",
            pay_for=["Усыпление не союзной роли"],
            limitations=[
                CANT_CHOOSE_IN_ROW,
                "Если жертва может делать ходы ночью после смерти, "
                f"то она не может быть усыплена ({Angel.pretty_role})",
            ],
            features=[
                "Ход жертвы отменяется полностью, поэтому она "
                "может выбрать одного и того же игрока дважды",
                f"Если усыпляет {Mafia.pretty_role}, то все мафии бездействуют ночью",
            ],
        )

    def __init__(self):
        super().__init__()
        self.was_euthanized: bool = False

    @get_processed_user_id_if_exists
    async def procedure_after_night(
        self,
        game_data: GameCache,
        processed_user_id: UserIdInt,
        **kwargs,
    ):
        user_role = game_data["players"][str(processed_user_id)][
            "role_id"
        ]
        role: RoleABC = self.all_roles[user_role]
        if isinstance(role, ActiveRoleAtNightABC) is False:
            return
        send_message = role.cancel_actions(
            game_data=game_data, user_id=processed_user_id
        )
        if send_message:
            self.was_euthanized = True
            with suppress(TelegramAPIError):
                await self.bot.send_message(
                    chat_id=processed_user_id,
                    text=make_build(
                        "😴Сложно поверить, но все твои действия ночью были лишь сном!"
                    ),
                    protect_content=game_data["settings"][
                        "protect_content"
                    ],
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
        if self.was_euthanized is False:
            return
        if processed_role.grouping == Groupings.civilians:
            money = 0
        else:
            money = int(processed_role.payment_for_murder * 1.5)
        self.add_money_to_all_allies(
            game_data=game_data,
            money=money,
            user_url=user_url,
            processed_role=processed_role,
            beginning_message="Усыпление",
        )
        self.was_euthanized = False
