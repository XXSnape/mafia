from cache.cache_types import GameCache
from services.game.roles.base.mixins import SuicideRoleMixin
from general.groupings import Groupings
from services.game.roles.base import Role


class Masochist(SuicideRoleMixin, Role):
    role = "Мазохист"
    photo = "https://i.pinimg.com/736x/14/a5/f5/14a5f5eb5dbd73c4707f24d436d80c0b.jpg"
    grouping = Groupings.other
    purpose = "Тебе нужно умереть на дневном голосовании."

    async def report_death(
        self, game_data: GameCache, is_night: bool, user_id: int
    ):
        if is_night is False:
            message = "Поздравляем! Тебя линчевали на голосовании, как ты и хотел!"
            await self.bot.send_message(
                chat_id=user_id, text=message
            )
            self._winners.append(user_id)
            return
        await super().report_death(
            game_data=game_data, is_night=is_night, user_id=user_id
        )
