from cache.cache_types import GameCache, RolesLiteral, UserIdInt
from cache.extra import ExtraCache
from mafia.roles.base import ActiveRoleAtNightABC
from mafia.roles.base.mixins import ProcedureAfterNightABC
from mafia.roles.base.roles import RoleABC
from mafia.roles.descriptions.description import RoleDescription
from mafia.roles.descriptions.texts import (
    CANT_CHOOSE_IN_ROW,
)
from states.game import UserFsm
from utils.informing import send_a_lot_of_messages_safely
from utils.roles import (
    get_processed_role_and_user_if_exists,
    get_processed_user_id_if_exists,
)


class Journalist(ProcedureAfterNightABC, ActiveRoleAtNightABC):
    role = "Журналист"
    role_id: RolesLiteral = "journalist"
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

    @property
    def role_description(self) -> RoleDescription:
        return RoleDescription(
            skill="Узнает людей, которые приходили к жертве ночью",
            pay_for=["Количество людей, пришедших к жертве"],
            limitations=[
                CANT_CHOOSE_IN_ROW,
                "Может делать ход только на чётную ночь",
            ],
        )

    @get_processed_user_id_if_exists
    async def procedure_after_night(
        self,
        game_data: GameCache,
        processed_user_id: UserIdInt,
        **kwargs,
    ):
        interacting = [
            game_data["players"][str(user_id)]["url"]
            for user_id in game_data["tracking"]
            .get(str(processed_user_id), {})
            .get("interacting", [])
            if user_id not in game_data[self.roles_key]
        ]
        self.number_of_visitors = len(interacting)
        visitors = ", ".join(interacting)
        user_url = game_data["players"][str(processed_user_id)][
            "url"
        ]
        text = (
            f"{user_url} сегодня никто не навещал"
            if not visitors
            else f"К {user_url} приходили: {visitors}"
        )
        await send_a_lot_of_messages_safely(
            bot=self.bot,
            users=game_data[self.roles_key],
            text=text,
            protect_content=game_data["settings"]["protect_content"],
        )

    @get_processed_role_and_user_if_exists
    async def accrual_of_overnight_rewards(
        self,
        game_data: GameCache,
        user_url: str,
        processed_user_id: int,
        processed_role: RoleABC,
        **kwargs,
    ):
        if self.number_of_visitors == 0:
            return

        money = 6 * self.number_of_visitors
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

    def allow_sending_mailing(self, game_data: GameCache):
        if game_data["number_of_night"] % 2 == 0:
            return True
