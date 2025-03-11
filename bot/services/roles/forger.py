from cache.cache_types import ExtraCache, GameCache
from cache.roleses import Groupings
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

    async def procedure_after_night(self, game_data: GameCache):
        if (
            game_data["disclosed_roles"]
            and game_data["forged_roles"]
        ):
            game_data["disclosed_roles"][:] = game_data[
                "forged_roles"
            ]

    def cancel_actions(self, game_data: GameCache, user_id: int):
        if game_data["forged_roles"]:
            game_data["forged_roles"].clear()
            return True
        return False

    def __init__(self):
        self.state_for_waiting_for_action = UserFsm.FORGER_FAKES
