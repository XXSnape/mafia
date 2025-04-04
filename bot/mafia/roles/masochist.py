from cache.cache_types import GameCache
from mafia.roles.base.mixins import SuicideRoleMixin
from general.groupings import Groupings
from mafia.roles.base import RoleABC
from utils.pretty_text import make_build


class Masochist(SuicideRoleMixin, RoleABC):
    role = "Мазохист"
    role_id = "masochist"
    photo = "https://i.pinimg.com/736x/14/a5/f5/14a5f5eb5dbd73c4707f24d436d80c0b.jpg"
    grouping = Groupings.other
    purpose = "Тебе нужно умереть на дневном голосовании."

    async def report_death(
        self, game_data: GameCache, at_night: bool, user_id: int
    ):
        if at_night is False:
            message = make_build(
                "Поздравляем! Тебя линчевали на голосовании, как ты и хотел!"
            )
            await self.bot.send_message(
                chat_id=user_id, text=message
            )
            self._winners.append(user_id)
            return
        await super().report_death(
            game_data=game_data, at_night=at_night, user_id=user_id
        )
