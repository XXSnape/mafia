from cache.cache_types import GameCache
from services.roles.base import ActiveRoleAtNight
from cache.roleses import Groupings
from states.states import UserFsm


class Killer(ActiveRoleAtNight):
    role = "Наёмный убийца"
    need_to_monitor_interaction = False
    photo = "https://steamuserimages-a.akamaihd.net/ugc/633105202506112549/"
    "988D53D1D6BF2FAC4665E453F736C438F601DF6D/"
    "?imw=512&imh=512&ima=fit&impolicy=Letterbox&imcolor=%23000000&letterbox=true"
    grouping = Groupings.criminals
    purpose = "Ты убиваешь, кого захочешь, а затем восстанавливаешь свои силы целую ночь."
    message_to_group_after_action = (
        "ЧВК продолжают работать на территории города!"
    )
    message_to_user_after_action = "Ты решился ликвидировать {url}"
    mail_message = "Реши, кому поможешь этой ночью решить проблемы и убить врага!"
    can_kill_at_night = True

    def __init__(self):
        self.state_for_waiting_for_action = UserFsm.KILLER_ATTACKS

    async def mailing(self, game_data: GameCache):
        if game_data["number_of_night"] % 2 != 0:
            await super().mailing(game_data)
