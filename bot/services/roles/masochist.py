from cache.cache_types import GameCache
from services.roles.base import Role
from cache.roleses import Groupings


class Masochist(Role):
    role = "Мазохист"
    photo = "https://i.pinimg.com/736x/14/a5/f5/14a5f5eb5dbd73c4707f24d436d80c0b.jpg"
    grouping = Groupings.masochists
    purpose = "Тебе нужно умереть на дневном голосовании."

    async def report_death(
        self, game_data: GameCache, is_night: bool, user_id: int
    ):
        if is_night is False:
            message = "Поздравляем! Тебя линчевали на голосовании, как ты и хотел!"
            await self.bot.send_message(
                chat_id=user_id, text=message
            )
            game_data["winners"].append(user_id)
        await super().report_death(
            game_data=game_data, is_night=is_night, user_id=user_id
        )
