from cache.cache_types import ExtraCache, GameCache
from services.roles.base.roles import Groupings
from services.roles.base import ActiveRoleAtNight
from states.states import UserFsm


class Instigator(ActiveRoleAtNight):
    role = "Подстрекатель"
    photo = "https://avatars.dzeninfra.ru/get-zen_doc/3469057/pub_620655d2a7947c53d6c601a2_620671b4b495be46b12c0a0c/scale_1200"
    grouping = Groupings.civilians
    purpose = (
        "Твоя жертва всегда ошибется при выборе на голосовании."
    )
    message_to_group_after_action = "Кажется, кто-то становится жертвой психологического насилия!"
    mail_message = "Кого надоумить на неправильный выбор?"
    notification_message = None
    payment_for_treatment = 7
    payment_for_murder = 11
    extra_data = [ExtraCache(key="deceived")]

    def __init__(self):
        self.state_for_waiting_for_action = (
            UserFsm.INSTIGATOR_CHOOSES_SUBJECT
        )

    def cancel_actions(self, game_data: GameCache, user_id: int):
        game_data[self.extra_data.key].clear()
        super().cancel_actions(game_data=game_data, user_id=user_id)
