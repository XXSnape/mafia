from cache.cache_types import GameCache, RolesLiteral, UserIdInt
from general.groupings import Groupings
from utils.pretty_text import make_build

from mafia.roles.base import RoleABC
from mafia.roles.base.mixins import SuicideRoleMixin
from mafia.roles.descriptions.description import RoleDescription
from mafia.roles.descriptions.texts import (
    DONT_PAY_FOR_NIGHTS,
    DONT_PAY_FOR_VOTING,
    PAY_FOR_EARLY_DEATH,
)


class Masochist(SuicideRoleMixin, RoleABC):
    role = "Мазохист"
    role_id: RolesLiteral = "masochist"
    photo = "https://i.pinimg.com/736x/14/a5/f5/14a5f5eb5dbd73c4707f24d436d80c0b.jpg"
    grouping = Groupings.other
    purpose = "Тебе нужно умереть на дневном голосовании."

    @property
    def role_description(self) -> RoleDescription:
        return RoleDescription(
            skill=None,
            pay_for=["Смерть днём"],
            limitations=[DONT_PAY_FOR_NIGHTS, DONT_PAY_FOR_VOTING],
            features=[PAY_FOR_EARLY_DEATH],
            wins_if="Побеждает, если умрёт днём",
        )

    async def report_death(
        self,
        game_data: GameCache,
        at_night: bool,
        user_id: UserIdInt,
        message_if_died_especially: str | None = None,
    ):
        if at_night is False:
            self._winners.append(user_id)
            message = make_build(
                "🥳Поздравляем! Тебя линчевали на голосовании, как ты и хотел!"
            )
            await self.bot.send_message(
                chat_id=user_id,
                text=message,
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
