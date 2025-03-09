from cache.cache_types import GameCache
from cache.roleses import Groupings
from services.roles.base import Role


class SuicideBomber(Role):
    role = "Ночной смертник"
    photo = "https://sun6-22.userapi.com/impg/zAaADEA19scv86EFl8bY1wUYRCJyBPGg1qamiA/xjMRCUhA20g.jpg?"
    "size=1280x1280&quality=96&"
    "sign=de22e32d9a16e37a3d46a2df767eab0b&c_uniq_tag="
    "EOC9ErRHImjvmda4Qd5Pq59HPf-wUgr77rzHZvabHjc&type=album"
    grouping = Groupings.suicide_bombers
    purpose = "Тебе нужно умереть ночью."

    async def report_death(
        self, game_data: GameCache, is_night: bool, user_id: int
    ):
        if is_night is True:
            message = "Поздравляем! Тебя убили ночью, как ты и хотел. Обязательно поглумись над мафией"
            await self.bot.send_message(
                chat_id=user_id, text=message
            )
            game_data["winners"].append(user_id)
        await super().report_death(
            game_data=game_data, is_night=is_night, user_id=user_id
        )
