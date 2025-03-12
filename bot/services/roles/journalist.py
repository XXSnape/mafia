from cache.cache_types import ExtraCache, GameCache
from services.roles.base.roles import Groupings, Role
from services.roles.base import ActiveRoleAtNight
from services.roles.base.mixins import ProcedureAfterNight
from states.states import UserFsm
from utils.validators import (
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
        self, game_data: GameCache, processed_user_id: int
    ):
        visitors = ", ".join(
            game_data["players"][str(user_id)]["url"]
            for user_id in game_data["tracking"]
            .get(str(processed_user_id), {})
            .get("interacting", [])
            if user_id != game_data[self.roles_key][0]
        )
        user_url = game_data["players"][str(processed_user_id)][
            "url"
        ]
        message = (
            f"{user_url} сегодня никто не навещал"
            if not visitors
            else f"К {user_url} приходили: {visitors}"
        )
        await self.bot.send_message(
            chat_id=game_data[self.roles_key][0], text=message
        )

    @get_processed_role_and_user_if_exists
    async def accrual_of_overnight_rewards(
        self,
        *,
        game_data: GameCache,
        all_roles: dict[str, Role],
        user_url: str,
        processed_user_id: int,
        processed_role: Role,
    ):
        visitors = (
            len(
                game_data["tracking"]
                .get(str(processed_user_id), {})
                .get("interacting", [])
            )
            - 1
        )
        if not visitors:
            return
        money = 4 * visitors
        for journalist_id in game_data[self.roles_key]:
            game_data["players"][str(journalist_id)][
                "money"
            ] += money
            game_data["players"][str(journalist_id)][
                "achievements"
            ].append(
                f'Ночь {game_data["number_of_night"]}.'
                f"Интервью с {user_url} - {money}💵"
            )

    def __init__(self):
        self.state_for_waiting_for_action = (
            UserFsm.JOURNALIST_TAKES_INTERVIEW
        )
