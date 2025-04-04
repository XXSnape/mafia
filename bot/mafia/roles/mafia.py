from cache.cache_types import GameCache
from general.text import ATTEMPT_TO_KILL
from utils.common import save_notification_message
from mafia.roles.base.roles import RoleABC
from general.groupings import Groupings
from mafia.roles.base import (
    ActiveRoleAtNightABC,
    AliasRoleABC,
)
from mafia.roles.base.mixins import (
    MurderAfterNightABC,
)
from states.states import UserFsm
from utils.roles import get_processed_role_and_user_if_exists


class Mafia(MurderAfterNightABC, ActiveRoleAtNightABC):
    role = "Дон. Высшее звание в преступных группировках"
    role_id = "don"
    photo = (
        "https://avatars.mds.yandex.net/i?id="
        "a7b2f1eed9cca869784091017f8a66ff_l-7677819-images-thumbs&n=13"
    )
    grouping = Groupings.criminals
    purpose = "Тебе нужно руководить преступниками и убивать мирных."
    message_to_group_after_action = "Мафия выбрала жертву!"
    message_to_user_after_action = "Ты выбрал убить {url}"
    mail_message = "Кого убить этой ночью?"
    need_to_monitor_interaction = False
    payment_for_treatment = 0
    payment_for_murder = 20
    notification_message = None

    def __init__(self):
        self.state_for_waiting_for_action = UserFsm.MAFIA_ATTACKS

    @get_processed_role_and_user_if_exists
    async def accrual_of_overnight_rewards(
        self,
        game_data: GameCache,
        victims: set[int],
        processed_role: RoleABC,
        user_url: str,
        processed_user_id: int,
        **kwargs
    ):
        save_notification_message(
            game_data=game_data,
            processed_user_id=processed_user_id,
            message=ATTEMPT_TO_KILL,
            current_user_id=None,
        )
        if processed_user_id not in victims:
            return
        money = (
            0
            if processed_role.grouping == Groupings.criminals
            else processed_role.payment_for_murder
        )
        self.add_money_to_all_allies(
            game_data=game_data,
            money=money,
            user_url=user_url,
            processed_role=processed_role,
            beginning_message="Убийство",
        )


class MafiaAlias(AliasRoleABC, Mafia):
    role = "Мафия"
    role_id = "mafia"
    photo = "https://i.pinimg.com/736x/a1/10/db/a110db3eaba78bf6423bcea68f330a64.jpg"
    purpose = (
        "Тебе нужно уничтожить всех горожан и подчиняться дону."
    )
    is_mass_mailing_list = True
    message_to_user_after_action = (
        "Ты выбрал убить {url}. Но Дон может принять другое решение."
    )
    payment_for_treatment = 0
    payment_for_murder = 13
