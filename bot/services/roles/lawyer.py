from services.roles.base import ActiveRoleAtNight
from cache.roleses import Groupings
from states.states import UserFsm


class Lawyer(ActiveRoleAtNight):
    role = "Адвокат"
    mail_message = "Кого защитить на голосовании?"
    do_not_choose_self = 2
    photo = "https://avatars.mds.yandex.net/get-altay/"
    "5579175/2a0000017e0aa51c3c1fd887206b0156ee34/XXL_height"
    grouping = Groupings.civilians
    purpose = "Тебе нужно защитить мирных жителей от своих же на голосовании."
    message_to_group_after_action = (
        "Кому-то обеспечена защита лучшими адвокатами города!"
    )
    message_to_user_after_action = "Ты выбрал защитить {url}"

    def __init__(self):
        self.state_for_waiting_for_action = UserFsm.LAWYER_PROTECTS
