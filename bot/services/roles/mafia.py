from cache.cache_types import GameCache
from services.roles.base.roles import Groupings, Role
from services.roles.base import (
    ActiveRoleAtNight,
    AliasRole,
    BossIsDeadMixin,
)
from services.roles.base.mixins import (
    MurderAfterNight,
)
from states.states import UserFsm
from utils.validators import get_processed_role_and_user_if_exists


class MafiaAlias(AliasRole):
    role = "Мафия"
    photo = "https://i.pinimg.com/736x/a1/10/db/a110db3eaba78bf6423bcea68f330a64.jpg"
    purpose = (
        "Тебе нужно уничтожить всех горожан и подчиняться дону."
    )
    is_mass_mailing_list = True
    message_to_user_after_action = (
        "Ты выбрал убить {url}. Но Дон может принять другое решение."
    )
    grouping = Groupings.criminals
    notification_message = None
    payment_for_treatment = 0
    payment_for_murder = 13

    def __init__(self):
        self.state_for_waiting_for_action = UserFsm.MAFIA_ATTACKS

    @classmethod
    @property
    def roles_key(cls):
        return Mafia.roles_key

    @classmethod
    @property
    def processed_users_key(cls):
        return Mafia.processed_users_key

    @classmethod
    @property
    def last_interactive_key(cls):
        return Mafia.last_interactive_key


class Mafia(MurderAfterNight, BossIsDeadMixin, ActiveRoleAtNight):
    role = "Дон. Высшее звание в преступных группировках"
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
    can_kill_at_night = True
    notification_message = None
    payment_for_treatment = 0
    payment_for_murder = 20

    alias = MafiaAlias()

    def __init__(self):
        self.state_for_waiting_for_action = UserFsm.MAFIA_ATTACKS

    @get_processed_role_and_user_if_exists
    async def accrual_of_overnight_rewards(
        self,
        *,
        game_data: GameCache,
        all_roles: dict[str, Role],
        victims: set[int],
        processed_role: Role,
        user_url: str,
        processed_user_id: int,
    ):
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
