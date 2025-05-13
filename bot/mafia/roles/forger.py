from cache.cache_types import GameCache, RolesLiteral, UserIdInt
from cache.extra import ExtraCache
from general.groupings import Groupings
from general.text import (
    ROLE_IS_KNOWN,
)
from mafia.roles.base import ActiveRoleAtNightABC
from mafia.roles.base.mixins import (
    MafiaConverterABC,
    ProcedureAfterNightABC,
)
from mafia.roles.descriptions.description import RoleDescription
from mafia.roles.descriptions.texts import (
    CAN_CHOOSE_YOURSELF,
)
from states.game import UserFsm


class Forger(
    MafiaConverterABC, ProcedureAfterNightABC, ActiveRoleAtNightABC
):
    role = "Румпельштильцхен"
    role_id: RolesLiteral = "forger"
    grouping = Groupings.criminals
    purpose = (
        "Ты должен обманывать местную полицию и "
        "подделывать документы на свое усмотрение во имя мафии"
    )
    message_to_group_after_action = (
        "Говорят, в лесах завелись персонажи из Шрека, "
        "подговорённые мафией, дискоординирующие государственную армию!"
    )
    photo = (
        "https://sun9-64.userapi.com/impg/R8WBtzZkQKycXD"
        "W5YCvKXUJB03XJnboRa0LDHw/yo9Ng0yPqa0.jpg?"
        "size=604x302&quality=95&sign"
        "=0fb255f26d2fd1775b2db1c2001f7a0b&type=album"
    )
    do_not_choose_self = 2
    do_not_choose_others = 2
    mail_message = "Кому сегодня подделаешь документы?"
    extra_data = [ExtraCache(key="forged_roles")]
    need_to_monitor_interaction = False
    is_self_selecting = True
    notification_message = ROLE_IS_KNOWN
    payment_for_treatment = 0
    payment_for_murder = 16

    @property
    def role_description(self) -> RoleDescription:
        from .policeman import Policeman

        return RoleDescription(
            skill="Может подменить документы любому игроку на любую роль, которая есть в игре",
            pay_for=[
                "Подмену документов игроку, которого проверили"
            ],
            limitations=[
                "Не может подменить документы игроку на роль, которая может эту роль раскрыть",
            ],
            features=[
                f"Становится мафией после смерти {Policeman.pretty_role} и его союзников по роли",
                "Во время Тумана Войны может подменить документы на роль, которая была в игре",
                CAN_CHOOSE_YOURSELF,
            ],
        )

    def get_processed_user_id(self, game_data: GameCache):
        if len(game_data["forged_roles"]) == 2:
            return game_data["forged_roles"][0]

    async def procedure_after_night(
        self, game_data: GameCache, **kwargs
    ):
        from .policeman import Policeman
        from .warden import Warden

        forged_roles = game_data["forged_roles"]
        if len(forged_roles) != 2:
            return
        forged_user_id, forged_role_id = forged_roles
        disclosed_roles = game_data.get("disclosed_roles")
        user_role_id = game_data["players"][str(forged_user_id)][
            "role_id"
        ]
        if disclosed_roles:
            user_id = disclosed_roles[0]
            if (
                user_id == forged_user_id
                and user_role_id != forged_role_id
            ):
                self.has_policeman_been_deceived = True
                self.all_roles[Policeman.role_id].temporary_roles[
                    forged_user_id
                ] = forged_role_id

        checked = game_data.get("checked_for_the_same_groups", [])
        if len(checked) != 2:
            return
        if (
            forged_user_id in checked
            and self.all_roles[user_role_id].grouping
            != self.all_roles[forged_role_id].grouping
        ):
            self.has_warden_been_deceived = True
            self.all_roles[Warden.role_id].temporary_roles[
                forged_user_id
            ] = forged_role_id

    async def accrual_of_overnight_rewards(
        self, game_data: GameCache, victims: set[UserIdInt], **kwargs
    ):
        from .policeman import Policeman
        from .warden import Warden

        deceived_users = []
        if self.has_policeman_been_deceived:
            policeman = game_data[Policeman.roles_key][0]
            url = game_data["players"][str(policeman)]["url"]
            money = 14
            deceived_users.append([url, money, Policeman()])

        if self.has_warden_been_deceived:
            warden = game_data[Warden.roles_key][0]
            url = game_data["players"][str(warden)]["url"]
            money = 10
            deceived_users.append([url, money, Warden()])

        self.has_policeman_been_deceived = False
        self.has_warden_been_deceived = False

        for url, money, role in deceived_users:
            self.add_money_to_all_allies(
                game_data=game_data,
                money=money,
                user_url=url,
                processed_role=role,
                beginning_message="Спецоперация по подделке документов прошла успешно. Обманут",
            )

    def check_for_possibility_to_transform(
        self, game_data: GameCache
    ):
        from .policeman import Policeman

        policeman = game_data.get(Policeman.roles_key)
        if not policeman:
            return game_data[self.roles_key]

    def cancel_actions(self, game_data: GameCache, user_id: int):
        if game_data["forged_roles"]:
            game_data["forged_roles"].clear()
        return super().cancel_actions(
            game_data=game_data, user_id=user_id
        )

    def __init__(self):
        self.state_for_waiting_for_action = UserFsm.FORGER_FAKES
        self.has_policeman_been_deceived = False
        self.has_warden_been_deceived = False
