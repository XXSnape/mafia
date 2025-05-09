from cache.cache_types import GameCache, RolesLiteral, UserIdInt
from cache.extra import ExtraCache
from mafia.roles.base import ActiveRoleAtNightABC, RoleABC
from mafia.roles.base.mixins import ProcedureAfterNightABC
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


class Agent(ProcedureAfterNightABC, ActiveRoleAtNightABC):
    role = "Агент 008"
    role_id: RolesLiteral = "agent"
    mail_message = "За кем следить этой ночью?"
    photo = (
        "https://avatars.mds.yandex.net/i?"
        "id=7b6e30fff5c795d560c07b69e7e9542f044fcaf9e04d"
        "4a31-5845211-images-thumbs&n=13"
    )
    purpose = "Ты можешь следить за кем-нибудь ночью"
    message_to_group_after_action = "Спецслужбы выходят на разведку"
    message_to_user_after_action = "Ты выбрал следить за {url}"
    extra_data = [
        ExtraCache(key="tracking", data_type=dict),
    ]

    @property
    def role_description(self) -> RoleDescription:
        return RoleDescription(
            skill="Узнает имена тех, к кому приходила ночью его жертва. "
            "Иными словами, узнает жертв своей жертвы",
            pay_for=[
                "Количество игроков, к которому приходила жертва"
            ],
            limitations=[CANT_CHOOSE_IN_ROW],
        )

    @get_processed_user_id_if_exists
    async def procedure_after_night(
        self,
        game_data: GameCache,
        processed_user_id: UserIdInt,
        **kwargs,
    ):
        sufferers = [
            game_data["players"][str(user_id)]["url"]
            for user_id in game_data["tracking"]
            .get(str(processed_user_id), {})
            .get("sufferers", [])
        ]
        visitors = ", ".join(sufferers)
        self.number_of_visitors = len(sufferers)
        user_url = game_data["players"][str(processed_user_id)][
            "url"
        ]
        text = (
            f"{user_url} cегодня ни к кому не ходил"
            if not visitors
            else f"{user_url} навещал: {visitors}"
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
        processed_role: RoleABC,
        user_url: str,
        processed_user_id: UserIdInt,
        **kwargs,
    ):
        if self.number_of_visitors == 0:
            return
        money = 6 * self.number_of_visitors
        self.add_money_to_all_allies(
            game_data=game_data,
            money=money,
            beginning_message="Слежка за",
            user_url=user_url,
            processed_role=processed_role,
        )
        self.number_of_visitors = 0

    def __init__(self):
        self.state_for_waiting_for_action = UserFsm.AGENT_WATCHES
        self.number_of_visitors = 0
