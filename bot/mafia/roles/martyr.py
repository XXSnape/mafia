from cache.cache_types import GameCache, RolesLiteral, UserIdInt
from general import settings
from general.groupings import Groupings
from general.text import NUMBER_OF_NIGHT, ROLE_IS_KNOWN
from mafia.roles import ActiveRoleAtNightABC, RoleABC
from mafia.roles.base.mixins import (
    ProcedureAfterNightABC,
    SunsetKillerABC,
)
from mafia.roles.descriptions.description import RoleDescription
from utils.informing import send_a_lot_of_messages_safely
from utils.roles import (
    get_processed_role_and_user_if_exists,
)


class Martyr(
    SunsetKillerABC,
    ProcedureAfterNightABC,
    ActiveRoleAtNightABC,
):
    role = "Мученик"
    role_id: RolesLiteral = "martyr"
    grouping = Groupings.civilians
    purpose = "Ты можешь отдать свою жизнь взамен на информацию о чей-либо роли"
    message_to_group_after_action = None
    photo = "https://i.pinimg.com/originals/aa/42/cf/aa42cfa177fad99b24ce22131f5b7869.jpg"
    mail_message = "За информацию о ком ты отдашь жизнь?"
    message_to_user_after_action = "Ты выбрал узнать роль {url} и умереть до начала следующей ночи"
    need_to_monitor_interaction = False
    notification_message = ROLE_IS_KNOWN
    payment_for_treatment = 10
    payment_for_murder = 14
    is_possible_to_skip_move = True
    number_in_order_after_sunset = 0

    @property
    def role_description(self) -> RoleDescription:
        return RoleDescription(
            skill="Может узнать роль любого игрока, но потом "
            "умрёт перед наступлением следующей ночи, если игра не завершится раньше",
            pay_for=["Проверку игрока"],
            features=["За более раннюю смерть платят больше"],
        )

    @get_processed_role_and_user_if_exists
    async def procedure_after_night(
        self,
        game_data: GameCache,
        processed_role: RoleABC,
        processed_user_id: UserIdInt,
        user_url: str,
        **kwargs,
    ):
        self.need_to_die = True
        await send_a_lot_of_messages_safely(
            bot=self.bot,
            users=game_data[self.roles_key],
            text=NUMBER_OF_NIGHT.format(game_data["number_of_night"])
            + f"{user_url} — {processed_role.pretty_role}",
            protect_content=game_data["settings"]["protect_content"],
        )

    @get_processed_role_and_user_if_exists
    async def accrual_of_overnight_rewards(
        self,
        game_data: GameCache,
        processed_role: RoleABC,
        processed_user_id: UserIdInt,
        user_url: str,
        **kwargs,
    ):
        money = max(
            (
                len(game_data["players"])
                // settings.mafia.minimum_number_of_players
            )
            * 100
            - (20 * game_data["number_of_night"]),
            0,
        )
        self.add_money_to_all_allies(
            game_data=game_data,
            money=money,
            user_url=user_url,
            processed_role=processed_role,
            beginning_message="Смерть за проверку",
        )

    def kill_after_all_actions(
        self,
        game_data: GameCache,
        current_inactive_users: list[UserIdInt],
        cured_users: list[UserIdInt],
    ) -> tuple[UserIdInt, str] | None:
        if self.need_to_die and game_data[self.roles_key]:
            self.need_to_die = False
            return (
                game_data[self.roles_key][0],
                "🫡Ты погиб во имя информации для своих союзников. Напиши последнее слово.",
            )
        return None

    def __init__(self):
        super().__init__()
        self.need_to_die: bool = False
