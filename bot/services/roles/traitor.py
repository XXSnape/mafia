from cache.cache_types import GameCache
from services.roles.base.roles import Groupings
from constants.output import ROLE_IS_KNOWN
from services.roles.base import ActiveRoleAtNight
from states.states import UserFsm


class Traitor(ActiveRoleAtNight):
    role = "Госизменщик"
    photo = "https://i.playground.ru/p/sLHLRFjDy8_89wYe26RIQw.jpeg"
    grouping = Groupings.criminals
    need_to_monitor_interaction = False
    purpose = "Ты можешь просыпаться каждую 2-ую ночь и узнавать роль других игроков для мафии."
    message_to_group_after_action = (
        "Мафия и Даркнет. Что может сочетаться лучше? "
        "Поддельные ксивы помогают узнавать правду!"
    )
    message_to_user_after_action = "Ты выбрал узнать роль {url}"
    mail_message = "Кого проверишь для мафии?"
    notification_message = ROLE_IS_KNOWN
    payment_for_treatment = 0
    payment_for_murder = 15

    def __init__(self):
        self.state_for_waiting_for_action = UserFsm.TRAITOR_FINDS_OUT

    async def mailing(self, game_data: GameCache):
        if game_data["number_of_night"] % 2 == 0:
            await super().mailing(game_data)
