import asyncio

from cache.cache_types import ExtraCache, GameCache
from services.game.roles.base.roles import Role
from services.game.roles.base import ActiveRoleAtNight
from services.game.roles.base.mixins import ProcedureAfterNight
from states.states import UserFsm
from utils.roles import (
    get_processed_user_id_if_exists,
    get_processed_role_and_user_if_exists,
)


class Journalist(ProcedureAfterNight, ActiveRoleAtNight):
    role = "Журналист"
    mail_message = "У кого взять интервью этой ночью?"
    photo = (
        "https://pics.rbc.ru/v2_companies_s3/resized/960xH/media/"
        "company_press_release_image/"
        "022eef78-63a5-4a2b-bb88-e4dcae639e34.jpg"
    )
    purpose = "Ты можешь приходить к местным жителям и узнавать, что они видели"
    message_to_group_after_action = (
        "Что случилось? Отчаянные СМИ спешат выяснить правду!"
    )
    message_to_user_after_action = "Ты выбрал взять интервью у {url}"
    extra_data = [
        ExtraCache(key="tracking", data_type=dict),
    ]
    payment_for_murder = 14

    @get_processed_user_id_if_exists
    async def procedure_after_night(
        self, game_data: GameCache, processed_user_id: int, **kwargs
    ):
        interacting = [
            game_data["players"][str(user_id)]["url"]
            for user_id in game_data["tracking"]
            .get(str(processed_user_id), {})
            .get("interacting", [])
            if user_id != game_data[self.roles_key][0]
        ]
        self.number_of_visitors = len(interacting) - 1
        visitors = ", ".join(interacting)
        user_url = game_data["players"][str(processed_user_id)][
            "url"
        ]
        message = (
            f"{user_url} сегодня никто не навещал"
            if not visitors
            else f"К {user_url} приходили: {visitors}"
        )
        await asyncio.gather(
            *(
                self.bot.send_message(chat_id=user_id, text=message)
                for user_id in game_data[self.roles_key]
            ),
            return_exceptions=True,
        )

    @get_processed_role_and_user_if_exists
    async def accrual_of_overnight_rewards(
        self,
        game_data: GameCache,
        user_url: str,
        processed_user_id: int,
        processed_role: Role,
        **kwargs,
    ):
        if self.number_of_visitors == 0:
            return

        money = 3 * self.number_of_visitors
        self.add_money_to_all_allies(
            game_data=game_data,
            money=money,
            user_url=user_url,
            processed_role=processed_role,
            beginning_message="Интервью с",
        )
        self.number_of_visitors = 0

    def __init__(self):
        self.state_for_waiting_for_action = (
            UserFsm.JOURNALIST_TAKES_INTERVIEW
        )
        self.number_of_visitors = 0
