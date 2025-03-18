from cache.cache_types import ExtraCache, GameCache
from services.roles.base.roles import Groupings, Role
from services.roles.base import ActiveRoleAtNight
from services.roles.base.mixins import ProcedureAfterNight
from states.states import UserFsm


class Forger(ProcedureAfterNight, ActiveRoleAtNight):
    role = "Румпельштильцхен"
    grouping = Groupings.criminals
    purpose = "Ты должен обманывать комиссара и подделывать документы на свое усмотрение во имя мафии"
    message_to_group_after_action = (
        "Говорят, в лесах завелись персонажи из Шрека, "
    )
    "подговорённые мафией, дискоординирующие государственную армию!"
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
        self, game_data: GameCache, **kwargs
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

    def cancel_actions(self, game_data: GameCache, user_id: int):
        if game_data["forged_roles"]:
            game_data["forged_roles"].clear()
            return True
        return False

    def __init__(self):
        self.state_for_waiting_for_action = UserFsm.FORGER_FAKES
