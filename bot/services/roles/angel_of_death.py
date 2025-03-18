from cache.cache_types import ExtraCache, GameCache
from services.roles.base.roles import Groupings, Role
from services.roles.base import ActiveRoleAtNight
from services.roles.base.mixins import (
    MurderAfterNight,
    ProcedureAfterVoting,
)
from states.states import UserFsm
from utils.validators import get_processed_role_and_user_if_exists


class AngelOfDeath(
    ProcedureAfterVoting, MurderAfterNight, ActiveRoleAtNight
):
    role = "Ангел смерти"
    mail_message = (
        "Глупые людишки тебя линчевали, кому ты отомстишь?"
    )
    need_to_monitor_interaction = False
    photo = "https://avatars.mds.yandex.net/get-entity_search/10844899/935958285/S600xU_2x"
    purpose = "Если ты умрешь на голосовании, сможешь ночью забрать кого-нибудь с собой"
    grouping = Groupings.other
    extra_data = [ExtraCache("angels_died", False)]
    message_to_user_after_action = "Ты выбрал отомстить {url}"
    can_kill_at_night = True
    payment_for_night_spent = 5

    async def take_action_after_voting(
        self, game_data: GameCache, removed_user: list[int], **kwargs
    ):
        removed_user_id = removed_user[0]
        if removed_user_id in game_data.get(self.roles_key, []):
            game_data["angels_died"].append(removed_user_id)

    @get_processed_role_and_user_if_exists
    async def accrual_of_overnight_rewards(
        self,
        game_data: GameCache,
        victims: set[int],
        processed_role: Role,
        user_url: str,
        processed_user_id: int,
        **kwargs
    ):
        if processed_user_id not in victims:
            return
        money = processed_role.payment_for_murder * 2
        self.add_money_to_all_allies(
            game_data=game_data,
            money=money,
            beginning_message="Отомщённое убийство",
            user_url=user_url,
            processed_role=processed_role,
        )

    def get_processed_user_id(self, game_data: GameCache):
        result = super().get_processed_user_id(game_data=game_data)
        if result:
            game_data["angels_died"].clear()
        return result

    async def report_death(
        self, game_data: GameCache, is_night: bool, user_id: int
    ):
        if is_night is False:
            await self.bot.send_message(
                chat_id=user_id,
                text="Тебя линчевали на голосовании, не забудь отомстить обидчикам!",
            )
            return
        await super().report_death(
            game_data=game_data, is_night=is_night, user_id=user_id
        )

    async def mailing(self, game_data: GameCache):
        if "angels_died" not in game_data:
            return
        current_number = game_data["number_of_night"]
        angels = []
        for angel_id in game_data["angels_died"]:
            if (
                current_number
                - game_data["players"][str(angel_id)][
                    "number_died_at_night"
                ]
            ) == 1:
                angels.append(angel_id)

        for angel_id in angels:
            await self.send_survey(
                player_id=angel_id, game_data=game_data
            )

    def __init__(self):
        self.state_for_waiting_for_action = (
            UserFsm.ANGEL_TAKES_REVENGE
        )
