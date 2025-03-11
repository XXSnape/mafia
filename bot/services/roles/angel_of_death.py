from cache.cache_types import ExtraCache, GameCache
from cache.roleses import Groupings
from services.roles.base import ActiveRoleAtNight
from services.roles.base.mixins import MurderAfterNight
from states.states import UserFsm


class AngelOfDeath(MurderAfterNight, ActiveRoleAtNight):
    role = "Ангел смерти"
    mail_message = (
        "Глупые людишки тебя линчевали, кому ты отомстишь?"
    )
    need_to_monitor_interaction = False
    photo = "https://avatars.mds.yandex.net/get-entity_search/10844899/935958285/S600xU_2x"
    purpose = "Если ты умрешь на голосовании, сможешь ночью забрать кого-нибудь с собой"
    grouping = Groupings.civilians
    extra_data = [ExtraCache("angels_died", False)]
    message_to_user_after_action = "Ты выбрал отомстить {url}"
    can_kill_at_night = True

    async def take_action_after_voting(
        self, game_data: GameCache, user_id: int | None
    ):
        if user_id in game_data.get(self.roles_key, []):
            game_data["angels_died"].append(user_id)

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
