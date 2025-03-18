from cache.cache_types import ExtraCache, GameCache
from services.roles.base import ActiveRoleAtNight, Role
from services.roles.base.mixins import ProcedureAfterNight
from states.states import UserFsm
from utils.validators import (
    get_processed_user_id_if_exists,
    get_processed_role_and_user_if_exists,
)


class Agent(ProcedureAfterNight, ActiveRoleAtNight):
    role = "Агент 008"
    mail_message = "За кем следить этой ночью?"
    photo = "https://avatars.mds.yandex.net/i?id=7b6e30fff5c795d560c07b69e7e9542f044fcaf9e04d4a31-5845211-images-thumbs&n=13"
    purpose = "Ты можешь следить за кем-нибудь ночью"
    message_to_group_after_action = "Спецслужбы выходят на разведу"
    message_to_user_after_action = "Ты выбрал следить за {url}"
    extra_data = [
        ExtraCache(key="tracking", data_type=dict),
    ]

    @get_processed_user_id_if_exists
    async def procedure_after_night(
        self,
        game_data: GameCache,
        processed_user_id: int,
        **kwargs,
    ):
        visitors = ", ".join(
            game_data["players"][str(user_id)]["url"]
            for user_id in game_data["tracking"]
            .get(str(processed_user_id), {})
            .get("sufferers", [])
        )
        user_url = game_data["players"][str(processed_user_id)][
            "url"
        ]
        message = (
            f"{user_url} cегодня ни к кому не ходил"
            if not visitors
            else f"{user_url} навещал: {visitors}"
        )
        await self.bot.send_message(
            chat_id=game_data[self.roles_key][0], text=message
        )

    @get_processed_role_and_user_if_exists
    async def accrual_of_overnight_rewards(
        self,
        game_data: GameCache,
        processed_role: Role,
        user_url: str,
        processed_user_id: int,
        **kwargs,
    ):
        visitors = len(
            game_data["tracking"]
            .get(str(processed_user_id), {})
            .get("sufferers", [])
        )
        if not visitors:
            return
        money = 6 * visitors
        self.add_money_to_all_allies(
            game_data=game_data,
            money=money,
            beginning_message="Слежка за",
            user_url=user_url,
            processed_role=processed_role,
        )

    def __init__(self):
        self.state_for_waiting_for_action = UserFsm.AGENT_WATCHES
