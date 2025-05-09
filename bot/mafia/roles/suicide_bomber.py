from cache.cache_types import GameCache, RolesLiteral
from general.groupings import Groupings
from mafia.roles.base import RoleABC
from mafia.roles.base.mixins import SuicideRoleMixin
from mafia.roles.descriptions.description import RoleDescription
from mafia.roles.descriptions.texts import (
    DONT_PAY_FOR_NIGHTS,
    DONT_PAY_FOR_VOTING,
    PAY_FOR_EARLY_DEATH,
)
from utils.pretty_text import make_build


class SuicideBomber(SuicideRoleMixin, RoleABC):
    role = "Ночной смертник"
    role_id: RolesLiteral = "suicide_bomber"
    photo = (
        "https://sun6-22.userapi.com/impg/zAaADEA19s"
        "cv86EFl8bY1wUYRCJyBPGg1qamiA/xjMRCUhA20g.jpg?size=1280x1280&quality=96&sign=de22e32d9a16e37a3d46a2df767eab0b&c_uniq_tag=EOC9ErRHImjvmda4Qd5Pq59HPf-wUgr77rzHZvabHjc&type=album"
    )
    grouping = Groupings.other
    purpose = "Тебе нужно умереть ночью."

    @property
    def role_description(self) -> RoleDescription:
        return RoleDescription(
            skill=None,
            pay_for=["Смерть ночью"],
            limitations=[DONT_PAY_FOR_NIGHTS, DONT_PAY_FOR_VOTING],
            features=[PAY_FOR_EARLY_DEATH],
            wins_if="Побеждает, если умрёт ночью",
        )

    async def report_death(
        self, game_data: GameCache, at_night: bool, user_id: int
    ):
        if at_night is True:
            message = make_build(
                "🥳Поздравляем! Тебя убили ночью, как ты и хотел. Обязательно поглумись над мафией"
            )
            await self.bot.send_message(
                chat_id=user_id,
                text=message,
                protect_content=game_data["settings"][
                    "protect_content"
                ],
            )
            self._winners.append(user_id)
            return
        await super().report_death(
            game_data=game_data, at_night=at_night, user_id=user_id
        )
