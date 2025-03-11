from cache.roleses import Groupings
from services.roles.base import ActiveRoleAtNight
from states.states import UserFsm


class Instigator(ActiveRoleAtNight):
    role = "Подстрекатель"
    photo = "https://avatars.dzeninfra.ru/get-zen_doc/3469057/pub_620655d2a7947c53d6c601a2_620671b4b495be46b12c0a0c/scale_1200"
    grouping = Groupings.other
    purpose = (
        "Твоя жертва всегда ошибется при выборе на голосовании."
    )
    message_to_group_after_action = "Кажется, кто-то становится жертвой психологического насилия!"
    message_to_user_after_action = (
        "Ты выбрал прополоскать мозги {url}"
    )
    mail_message = "Кого надоумить на неправильный выбор?"
    notification_message = None

    def __init__(self):
        self.state_for_waiting_for_action = UserFsm.INSTIGATOR_LYING
