from cache.cache_types import ExtraCache, GameCache
from constants.output import ROLE_IS_KNOWN
from general.groupings import Groupings
from mafia.roles.base import ActiveRoleAtNight
from mafia.roles.base.mixins import (
    ProcedureAfterNight,
    ProcedureAfterVoting,
)
from states.states import UserFsm
from utils.pretty_text import make_pretty
from utils.informing import notify_aliases_about_transformation
from utils.roles import (
    change_role,
)


class Forger(
    ProcedureAfterVoting, ProcedureAfterNight, ActiveRoleAtNight
):
    role = "Румпельштильцхен"
    role_id = "forger"
    grouping = Groupings.criminals
    purpose = "Ты должен обманывать местную полицию и подделывать документы на свое усмотрение во имя мафии"
    message_to_group_after_action = (
        "Говорят, в лесах завелись персонажи из Шрека, "
        "подговорённые мафией, дискоординирующие государственную армию!"
    )
    photo = (
        "https://sun9-64.userapi.com/impg/R8WBtzZkQKycXDW5YCvKXUJB03XJnboRa0LDHw/yo9Ng0yPqa0.jpg?"
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
    number_in_order_after_voting = 2

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
        self, game_data: GameCache, victims: set[int], **kwargs
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

    async def take_action_after_voting(
        self,
        game_data: GameCache,
        removed_user: list[int],
        **kwargs,
    ):
        from .policeman import Policeman
        from .mafia import MafiaAlias

        forgers = game_data[self.roles_key]
        if not forgers:
            return
        policeman = game_data.get(Policeman.roles_key)
        mafias = game_data.get(MafiaAlias.roles_key)

        if (
            (not policeman or policeman[0] == removed_user[0])
            and mafias
            and mafias[0] != removed_user[0]
        ):
            if MafiaAlias.role_id not in self.all_roles:
                mafia = MafiaAlias()
                mafia(
                    all_roles=self.all_roles,
                    dispatcher=self.dispatcher,
                    bot=self.bot,
                    state=self.state,
                )
                self.all_roles[MafiaAlias.role_id] = mafia
            forger_id = forgers[0]
            change_role(
                game_data=game_data,
                previous_role=self,
                new_role=MafiaAlias(),
                user_id=forger_id,
            )
            await notify_aliases_about_transformation(
                game_data=game_data,
                bot=self.bot,
                new_role=MafiaAlias(),
                user_id=forger_id,
            )
            await self.bot.send_photo(
                chat_id=game_data["game_chat"],
                photo=MafiaAlias.photo,
                caption=f"{make_pretty(self.role)} превращается в {make_pretty(MafiaAlias.role)}",
            )

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
