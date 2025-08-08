from typing import TYPE_CHECKING

from cache.cache_types import GameCache, RolesLiteral, UserIdInt
from cache.extra import ExtraCache
from general.groupings import Groupings
from general.text import (
    NUMBER_OF_NIGHT,
    ROLE_IS_KNOWN,
)
from keyboards.inline.keypads.mailing import (
    send_selection_to_players_kb,
)
from utils.common import get_criminals_ids
from utils.informing import send_a_lot_of_messages_safely
from utils.roles import get_processed_role_and_user_if_exists

from mafia.roles.base import ActiveRoleAtNightABC
from mafia.roles.base.mixins import (
    MafiaConverterABC,
    ProcedureAfterNightABC,
)
from mafia.roles.descriptions.description import RoleDescription
from mafia.roles.descriptions.texts import (
    CHECKING_PLAYER,
)

if TYPE_CHECKING:
    from mafia.roles import RoleABC


class Traitor(
    MafiaConverterABC, ProcedureAfterNightABC, ActiveRoleAtNightABC
):
    role = "Госизменщик"
    role_id: RolesLiteral = "traitor"
    photo = "https://i.playground.ru/p/sLHLRFjDy8_89wYe26RIQw.jpeg"
    grouping = Groupings.criminals
    need_to_monitor_interaction = False
    purpose = "Ты можешь узнавать роли других игроков и быть разведывательной силой мафии."
    message_to_group_after_action = (
        "Мафия и Даркнет. Что может сочетаться лучше? "
        "Поддельные ксивы помогают узнавать правду!"
    )
    message_to_user_after_action = "Ты выбрал узнать роль {url}"
    words_to_aliases_and_teammates = "Узнать роль"
    mail_message = "Кого проверишь для мафии?"
    notification_message = ROLE_IS_KNOWN
    payment_for_treatment = 0
    payment_for_murder = 15
    extra_data = [
        ExtraCache(
            key="mafias_are_shown",
            need_to_clear=False,
            data_type=list,
        ),
    ]

    @property
    def role_description(self) -> RoleDescription:
        return RoleDescription(
            skill="Узнаёт роль игрока и показывает её всем участникам группировки",
            pay_for=[CHECKING_PLAYER],
            features=[
                "Становится мафией после того, как узнал роли всех игроков",
            ],
        )

    @get_processed_role_and_user_if_exists
    async def procedure_after_night(
        self,
        game_data: GameCache,
        processed_role: "RoleABC",
        user_url: str,
        processed_user_id: UserIdInt,
        **kwargs,
    ):

        game_data["mafias_are_shown"].append(processed_user_id)
        text = NUMBER_OF_NIGHT.format(
            game_data["number_of_night"]
        ) + (
            f"❗️{self.pretty_role} проверил и узнал, "
            f"что {user_url} — {processed_role.pretty_role}!"
        )
        await send_a_lot_of_messages_safely(
            bot=self.bot,
            users=get_criminals_ids(game_data),
            text=text,
            protect_content=game_data["settings"]["protect_content"],
        )

    def check_for_possibility_to_transform(
        self, game_data: GameCache
    ):
        if set(game_data["mafias_are_shown"]).issuperset(
            set(game_data["live_players_ids"])
            - set(get_criminals_ids(game_data))
        ):
            return game_data[self.roles_key]

    def generate_markup(
        self,
        player_id: int,
        game_data: GameCache,
    ):
        return send_selection_to_players_kb(
            players_ids=game_data["live_players_ids"],
            players=game_data["players"],
            exclude=game_data["mafias_are_shown"]
            + get_criminals_ids(game_data),
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
        self.add_money_to_all_allies(
            game_data=game_data,
            money=10,
            beginning_message="Проверка",
            user_url=user_url,
            processed_role=processed_role,
        )
