from random import randint

from cache.cache_types import GameCache
from services.roles.base.roles import Groupings
from services.roles.base import Role
from services.roles.base.mixins import (
    ProcedureAfterNight,
)


class LuckyGay(ProcedureAfterNight, Role):
    role = "Везунчик"
    photo = "https://avatars.mds.yandex.net/get-mpic/5031100/img_id5520953584482126492.jpeg/orig"
    purpose = (
        "Возможно тебе повезет и ты останешься жив после покушения."
    )
    number_in_order = 2

    async def procedure_after_night(
        self,
        game_data: GameCache,
        recovered: list[int],
        murdered: list[int],
    ):
        send_to_group = False

        for lucky_id in game_data[self.roles_key]:
            if lucky_id in murdered:
                if randint(1, 10) in range(1, 5):
                    recovered.append(lucky_id)
                    game_data["messages_after_night"].append(
                        [lucky_id, "Тебе сегодня повезло"]
                    )
                    send_to_group = True
        if send_to_group:
            game_data["messages_after_night"].append(
                [game_data["game_chat"], "Кому - то сегодня повезло"]
            )

    # def treat(
    #     self,
    #     game_data: GameCache,
    #     recovered: list[int],
    #     murdered: list[int],
    # ):
    #     send_to_group = False
    #
    #     for lucky_id in game_data[self.roles_key]:
    #         if lucky_id in murdered:
    #             if randint(1, 10) in ():
    #                 recovered.append(lucky_id)
    #                 game_data["messages_after_night"].append(
    #                     [lucky_id, "Тебе сегодня повезло"]
    #                 )
    #                 send_to_group = True
    #     if send_to_group:
    #         game_data["messages_after_night"].append(
    #             [game_data["game_chat"], "Кому - то сегодня повезло"]
    #         )
