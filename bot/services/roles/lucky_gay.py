from random import randint

from cache.cache_types import GameCache
from cache.roleses import Groupings
from services.roles.base import Role
from services.roles.base.mixins import TreatmentMixin


class LuckyGay(TreatmentMixin, Role):
    role = "Везунчик"
    photo = "https://avatars.mds.yandex.net/get-mpic/5031100/img_id5520953584482126492.jpeg/orig"
    grouping = Groupings.civilians
    purpose = (
        "Возможно тебе повезет и ты останешься жив после покушения."
    )
    number_in_order_of_treatment = 2

    def treat(
        self,
        game_data: GameCache,
        recovered: list[int],
        murdered: list[int],
    ):
        send_to_group = False
        for lucky_id in game_data[self.roles_key]:
            if lucky_id in murdered:
                if randint(1, 10) in (1, 2, 3, 4):
                    recovered.append(lucky_id)
                    game_data["messages_after_night"].append(
                        [lucky_id, "Тебе сегодня повезло"]
                    )
                    send_to_group = True
        if send_to_group:
            game_data["messages_after_night"].append(
                [game_data["game_chat"], "Кому - то сегодня повезло"]
            )
