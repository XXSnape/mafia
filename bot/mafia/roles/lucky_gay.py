from random import randint

from cache.cache_types import GameCache, PlayersIds
from mafia.roles.descriptions.texts import PAYMENT_FOR_NIGHTS
from mafia.roles.base import RoleABC
from mafia.roles.base.mixins import (
    ProcedureAfterNightABC,
)
from mafia.roles.descriptions.description import RoleDescription


class LuckyGay(ProcedureAfterNightABC, RoleABC):
    role = "Везунчик"
    role_id = "lucky_gay"
    photo = "https://avatars.mds.yandex.net/get-mpic/5031100/img_id5520953584482126492.jpeg/orig"
    purpose = (
        "Возможно тебе повезет и ты останешься жив после покушения."
    )
    number_in_order_after_night = 2
    payment_for_treatment = 6
    payment_for_night_spent = 7

    @property
    def role_description(self) -> RoleDescription:
        return RoleDescription(
            skill="Мирный житель, который может с вероятностью 40% выжить после покушения на него ночью",
            pay_for=[PAYMENT_FOR_NIGHTS],
        )

    async def procedure_after_night(
        self,
        game_data: GameCache,
        recovered: PlayersIds,
        murdered: PlayersIds,
        **kwargs,
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
                [
                    game_data["game_chat"],
                    "✅Кому - то сегодня повезло",
                ]
            )

    async def accrual_of_overnight_rewards(
        self,
        **kwargs,
    ):
        return
