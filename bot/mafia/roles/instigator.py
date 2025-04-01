from cache.cache_types import ExtraCache, GameCache
from mafia.roles.base.mixins import ProcedureAfterVoting
from general.groupings import Groupings
from mafia.roles.base import ActiveRoleAtNight
from states.states import UserFsm
from utils.roles import get_user_role_and_url


class Instigator(ProcedureAfterVoting, ActiveRoleAtNight):
    role = "Подстрекатель"
    photo = "https://avatars.dzeninfra.ru/get-zen_doc/3469057/pub_620655d2a7947c53d6c601a2_620671b4b495be46b12c0a0c/scale_1200"
    grouping = Groupings.civilians
    purpose = "Твоя жертва проголосует за того, за кого прикажешь."
    message_to_group_after_action = (
        "Кажется, кому-то вправляют мозги!"
    )
    need_to_monitor_interaction = False
    mail_message = "Кого направить на правильный путь?"
    notification_message = None
    payment_for_treatment = 7
    payment_for_murder = 11
    extra_data = [ExtraCache(key="deceived")]

    def __init__(self):
        self.state_for_waiting_for_action = (
            UserFsm.INSTIGATOR_CHOOSES_SUBJECT
        )

    async def take_action_after_voting(
        self,
        game_data: GameCache,
        **kwargs,
    ):
        vote_for = game_data["vote_for"]
        deceived_user = game_data["deceived"]
        if len(deceived_user) != 2:
            return
        victim, aim = deceived_user
        if not [victim, aim] in vote_for:
            return
        role, url = get_user_role_and_url(
            game_data=game_data,
            processed_user_id=aim,
            all_roles=self.all_roles,
        )
        if role.grouping != Groupings.civilians:
            money = int(role.payment_for_murder // 1.5)
        else:
            money = 0
        self.add_money_to_all_allies(
            game_data=game_data,
            money=money,
            beginning_message="Помощь в голосовании за",
            user_url=url,
            processed_role=role,
            at_night=False,
        )

    def cancel_actions(self, game_data: GameCache, user_id: int):
        game_data["deceived"].clear()
        return super().cancel_actions(
            game_data=game_data, user_id=user_id
        )
