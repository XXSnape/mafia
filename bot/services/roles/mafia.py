from cache.cache_types import GameCache
from cache.roleses import Groupings
from services.roles.base import (
    ActiveRoleAtNight,
    AliasRole,
    BossIsDeadMixin,
)
from states.states import UserFsm
from utils.utils import get_the_most_frequently_encountered_id


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
    # state_for_waiting_for_action = UserFsm.MAFIA_ATTACKS

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


class Mafia(BossIsDeadMixin, ActiveRoleAtNight):
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

    alias = MafiaAlias()

    def get_victims(self, game_data: GameCache):
        victim_id = get_the_most_frequently_encountered_id(
            game_data[self.processed_users_key]
        )
        if victim_id is None:
            if not game_data[self.processed_users_key]:
                return set()
            if not game_data["killed_by_don"]:
                return set()
            return set(game_data["killed_by_don"])
        return {victim_id}

    def __init__(self):
        self.state_for_waiting_for_action = UserFsm.MAFIA_ATTACKS

    # alias = Alias(
    #     role=AliasesRole.mafia, is_mass_mailing_list=True
    # ),
