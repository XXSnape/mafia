from contextlib import suppress
from random import choice

from aiogram.exceptions import TelegramAPIError
from cache.cache_types import GameCache, RolesLiteral, UserIdInt
from general.groupings import Groupings
from mafia.roles.base import ActiveRoleAtNightABC
from mafia.roles.base.mixins import (
    ProcedureAfterNightABC,
    SunsetKillerABC,
)
from mafia.roles.descriptions.description import RoleDescription
from mafia.roles.descriptions.texts import (
    DONT_PAY_FOR_VOTING,
    GUARANTEED_TO_KILL,
)
from utils.pretty_text import make_build
from utils.roles import get_processed_user_id_if_exists


class Bride(
    SunsetKillerABC,
    ProcedureAfterNightABC,
    ActiveRoleAtNightABC,
):
    role = "Кровавая невеста"
    role_id: RolesLiteral = "bride"
    grouping = Groupings.other
    purpose = "Обязательно в первую ночь выбери жениха и делай все, чтобы он просто остался живым"
    message_to_group_after_action = (
        "Заключить брак любой может, но все ли умрут в один день?"
    )
    photo = "https://i.pinimg.com/736x/34/2b/eb/342bebbc1da7ac2937fc7555cc1e0e7f.jpg"
    mail_message = "Кого возьмешь в мужья?"
    message_to_user_after_action = (
        "Твой выбор пал на свадьбу с {url}"
    )
    need_to_monitor_interaction = False
    send_weekend_alerts = False
    notification_message = None
    payment_for_treatment = 5
    payment_for_murder = 13

    @property
    def role_description(self) -> RoleDescription:
        return RoleDescription(
            skill="В начале игры выбирает жениха (иначе проигрывает сразу) "
            "и оставшееся время делает всё возможное, чтобы суженый выжил. "
            "Если его убьют, Невеста так же умирает до наступления следующей ночи. "
            "Если Невесту убьют раньше, каждую чётную ночь случайным образом будут "
            "умирать жители города, но не жених. "
            "Это прекратится, когда погибнет избранник.",
            pay_for=[
                "Количество ночей, прожитых женихом, если он выжил"
            ],
            wins_if="Жених должен выжить",
            features=[
                "Жених узнает, что у него прошла свадьба, но не будет знать невесту",
                GUARANTEED_TO_KILL,
                "Ход не может быть отменён",
            ],
            limitations=[DONT_PAY_FOR_VOTING],
        )

    def get_money_for_victory_and_nights(
        self, game_data: GameCache, nights_lived: int, **kwargs
    ):
        if (
            self.groom_id is None
            or self.groom_id not in game_data["live_players_ids"]
        ):
            return 0, 0
        return game_data["number_of_night"] * 10, (
            self.payment_for_night_spent * nights_lived
        )

    @get_processed_user_id_if_exists
    async def procedure_after_night(
        self,
        game_data: GameCache,
        processed_user_id: UserIdInt,
        **kwargs
    ):
        self.groom_id = processed_user_id
        with suppress(TelegramAPIError):
            await self.bot.send_message(
                chat_id=self.groom_id,
                text=make_build(
                    "😅Тили-тили тесто, жених и невеста\n\n"
                    "У тебя появилась замечательная жена, "
                    "готовая оберегать тебя от всех бед!"
                ),
                protect_content=game_data["settings"][
                    "protect_content"
                ],
            )

    @staticmethod
    def allow_sending_mailing(game_data: GameCache):
        return game_data["number_of_night"] == 1

    async def accrual_of_overnight_rewards(self, **kwargs):
        return

    def kill_after_all_actions(
        self,
        game_data: GameCache,
        current_inactive_users: list[UserIdInt],
    ) -> tuple[UserIdInt, str] | None:

        if self.dropped_out or (
            len(current_inactive_users) != 0
            and any(
                game_data["players"][str(player_id)]["role_id"]
                == self.role_id
                for player_id in current_inactive_users
            )
        ):
            return None
        if self.groom_id is None and game_data[self.roles_key]:
            return (
                game_data[self.roles_key][0],
                "😡Ты выбываешь из игры, потому что жениха нужно выбирать обязательно в первую ночь! "
                "Можешь извиниться перед кандидатами.",
            )
        if (
            self.groom_id not in game_data["live_players_ids"]
            and game_data[self.roles_key]
        ):
            return (
                game_data[self.roles_key][0],
                "😢К сожалению, твой жених погиб, а ты с ним! Напиши последнее слово.",
            )
        if (
            not game_data[self.roles_key]
            and self.groom_id in game_data["live_players_ids"]
            and game_data["number_of_night"] % 2 == 0
        ):
            players = [
                user_id
                for user_id in game_data["live_players_ids"]
                if user_id != self.groom_id
            ]
            return (
                choice(players),
                "😢К сожалению, тебя убил дух разъярённой невесты. "
                "Ты можешь написать все, что думаешь по этому поводу.",
            )
        return None

    def cancel_actions(
        self, game_data: GameCache, user_id: UserIdInt
    ):
        return False

    def __init__(self):
        super().__init__()
        self.groom_id: UserIdInt | None = None
