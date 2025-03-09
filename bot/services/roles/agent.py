from cache.cache_types import ExtraCache, GameCache
from services.roles.base import ActiveRoleAtNight
from cache.roleses import Groupings
from states.states import UserFsm
from utils.validators import get_object_id_if_exists


class Agent(ActiveRoleAtNight):
    role = "Агент 008"
    need_to_monitor_interaction = True
    mail_message = "За кем следить этой ночью?"
    photo = "https://avatars.mds.yandex.net/i?id="
    "7b6e30fff5c795d560c07b69e7e9542f044fcaf9e04d4a31-5845211-images-thumbs&n=13"
    grouping = Groupings.civilians
    purpose = "Ты можешь следить за кем-нибудь ночью"
    message_to_group_after_action = "Спецслужбы выходят на разведу"
    message_to_user_after_action = "Ты выбрал следить за {url}"
    extra_data = [
        ExtraCache(key="tracking", data_type=dict),
    ]

    @get_object_id_if_exists
    async def send_delayed_messages_after_night(
        self, game_data: GameCache, user_id: int
    ):
        visitors = ", ".join(
            game_data["players"][str(user_id)]["url"]
            for user_id in game_data["tracking"]
            .get(str(user_id), {})
            .get("sufferers", [])
        )
        user_url = game_data["players"][str(user_id)]["url"]
        message = (
            f"{user_url} cегодня ни к кому не ходил"
            if not visitors
            else f"{user_url} навещал: {visitors}"
        )
        await self.bot.send_message(
            chat_id=game_data[self.roles_key][0], text=message
        )

    def __init__(self):
        self.state_for_waiting_for_action = UserFsm.AGENT_WATCHES
