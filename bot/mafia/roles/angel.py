import asyncio

from cache.cache_types import (
    GameCache,
    RolesLiteral,
    UserIdInt,
)
from general.groupings import Groupings
from mafia.roles.base import ActiveRoleAtNightABC
from mafia.roles.base.mixins import (
    FinisherOfNight,
    HealerAfterNightABC,
)
from mafia.roles.descriptions.description import RoleDescription
from mafia.roles.descriptions.texts import (
    PAYMENT_FOR_NIGHTS,
    SAVING_PLAYER,
)
from utils.pretty_text import make_build
from utils.state import reset_user_state


class Angel(
    FinisherOfNight,
    HealerAfterNightABC,
    ActiveRoleAtNightABC,
):
    role = "Ангел Хранитель"
    role_id: RolesLiteral = "angel"
    mail_message = "Ты здесь, чтобы помочь человечеству исправить ошибки! Кого ты излечишь?"
    need_to_monitor_interaction = False
    photo = "https://i.pinimg.com/736x/04/76/cd/0476cd1eb81fa8d31938bfb821f3b975.jpg"
    purpose = (
        "Если тебя линчуют на голосовании, "
        "сможешь следующей ночью кого-нибудь вылечить"
    )
    grouping = Groupings.civilians
    message_to_user_after_action = "Ты выбрал спасти {url}"
    message_to_group_after_action = (
        "Во имя добра и не думаешь о мести..."
    )
    payment_for_night_spent = 7
    clearing_state_after_death = False
    coefficient = 2
    additional_players_attr = "dead_angels"

    @property
    def role_description(self) -> RoleDescription:
        return RoleDescription(
            skill="Может вылечить любого, если его убьют днём",
            pay_for=[SAVING_PLAYER, PAYMENT_FOR_NIGHTS],
        )

    async def end_night(self, game_data: GameCache):
        for angel_id in self.dead_angels[:]:
            if (
                game_data["number_of_night"]
                == game_data["players"][str(angel_id)][
                    "number_died_at_night"
                ]
                + 1
            ):
                continue
            self.dead_angels.remove(angel_id)
            await reset_user_state(
                dispatcher=self.dispatcher,
                user_id=angel_id,
                bot_id=self.bot.id,
            )

    async def report_death(
        self,
        game_data: GameCache,
        at_night: bool,
        user_id: UserIdInt,
        message_if_died_especially: str | None = None,
    ):
        if at_night is False:
            self.dead_angels.append(user_id)
            await self.bot.send_message(
                chat_id=user_id,
                text=make_build(
                    "😢Тебя линчевали на голосовании, но ты не должен мстить, спаси товарищей!"
                ),
                protect_content=game_data["settings"][
                    "protect_content"
                ],
            )
            return
        await super().report_death(
            game_data=game_data,
            at_night=at_night,
            user_id=user_id,
            message_if_died_especially=message_if_died_especially,
        )

    async def mailing(self, game_data: GameCache):
        if not self.dead_angels:
            return
        await asyncio.gather(
            *(
                self.send_survey(
                    player_id=angel_id, game_data=game_data
                )
                for angel_id in self.dead_angels[:]
            ),
            return_exceptions=True,
        )

    def __init__(self):
        super().__init__()
        self.dead_angels = list[UserIdInt]()
