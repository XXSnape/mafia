from cache.cache_types import ExtraCache, GameCache
from services.roles.base.roles import Groupings, Role
from services.roles.base import ActiveRoleAtNight
from services.roles.base.mixins import (
    ProcedureAfterNight,
    ProcedureAfterVoting,
)
from states.states import UserFsm
from utils.utils import make_pretty
from utils.validators import (
    notify_aliases_about_transformation,
    change_role,
)


class Forger(
    ProcedureAfterVoting, ProcedureAfterNight, ActiveRoleAtNight
):
    role = "Румпельштильцхен"
    grouping = Groupings.criminals
    purpose = "Ты должен обманывать комиссара и подделывать документы на свое усмотрение во имя мафии"
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
    is_self_selecting = True
    notification_message = "Твои документы подделаны!"
    payment_for_treatment = 0
    payment_for_murder = 11
    number_in_order_after_voting = 2

    async def procedure_after_night(
        self, game_data: GameCache, **kwargs
    ):
        if (
            game_data["disclosed_roles"]
            and game_data["forged_roles"]
        ):
            game_data["disclosed_roles"][:] = game_data[
                "forged_roles"
            ]

    async def accrual_of_overnight_rewards(
        self, game_data: GameCache, victims: set[int], **kwargs
    ):
        from .policeman import Policeman

        if (
            game_data["disclosed_roles"]
            and game_data["disclosed_roles"]
            == game_data["forged_roles"]
        ):
            policeman = game_data[Policeman.roles_key][0]
            url = game_data["players"][str(policeman)]["url"]
            money = 14
            self.add_money_to_all_allies(
                game_data=game_data,
                money=money,
                user_url=url,
                processed_role=Policeman(),
                beginning_message="Спецоперация по подделке документов прошла успешно. Обманут",
            )

    async def take_action_after_voting(
        self,
        game_data: GameCache,
        removed_user: list[int],
        all_roles: dict[str, Role],
        **kwargs,
    ):
        from .policeman import Policeman
        from .mafia import MafiaAlias

        forgers = game_data[self.roles_key]
        if not forgers:
            return
        policeman = game_data[Policeman.roles_key]
        mafias = game_data[MafiaAlias.roles_key]

        if (
            (not policeman or policeman[0] == removed_user[0])
            and mafias
            and mafias[0] != removed_user[0]
        ):
            if "mafia" not in all_roles:
                mafia = MafiaAlias()
                mafia(
                    dispatcher=self.dispatcher,
                    bot=self.bot,
                    state=self.state,
                )
                all_roles["mafia"] = mafia
            forger_id = forgers[0]
            await notify_aliases_about_transformation(
                game_data=game_data,
                bot=self.bot,
                new_role=MafiaAlias(),
                user_id=forger_id,
            )
            change_role(
                game_data=game_data,
                previous_role=self,
                new_role=MafiaAlias(),
                role_key="mafia",
                user_id=forger_id,
            )
            await notify_aliases_about_transformation(
                game_data=game_data,
                bot=self.bot,
                new_role=MafiaAlias(),
                user_id=forger_id,
            )
            await self.bot.send_message(
                chat_id=game_data["game_chat"],
                text=f"{make_pretty(self.role)} превращается в {make_pretty(MafiaAlias.role)}",
            )

    def cancel_actions(self, game_data: GameCache, user_id: int):
        if game_data["forged_roles"]:
            game_data["forged_roles"].clear()
            return True
        return False

    def __init__(self):
        self.state_for_waiting_for_action = UserFsm.FORGER_FAKES
