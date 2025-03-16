from cache.cache_types import ExtraCache, GameCache
from constants.output import MONEY_SYM
from services.roles.base.roles import Groupings, Role
from services.roles.base import ActiveRoleAtNight
from states.states import UserFsm


class Instigator(ActiveRoleAtNight):
    role = "Подстрекатель"
    photo = "https://avatars.dzeninfra.ru/get-zen_doc/3469057/pub_620655d2a7947c53d6c601a2_620671b4b495be46b12c0a0c/scale_1200"
    grouping = Groupings.civilians
    purpose = "Твоя жертва проголосует за того, за кого прикажешь."
    message_to_group_after_action = "Кажется, кто-то становится жертвой психологического насилия!"
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
        all_roles: dict[str, Role],
        game_data: GameCache,
        user_id: int,
    ):
        vote_for = game_data["vote_for"]
        deceived_user = game_data[self.extra_data[0].key]
        if not deceived_user:
            return
        victim, aim = deceived_user[0]
        if not [victim, aim] in vote_for:
            return
        aim_data = game_data["players"][str(user_id)]
        role = all_roles[
            game_data["players"][str(user_id)]["enum_name"]
        ]
        number_of_day = game_data["number_of_night"]
        if role.grouping not in Groupings.civilians:
            money = role.payment_for_murder * 2
        else:
            money = 0
        for player_id in game_data[self.roles_key]:
            game_data["players"][str(player_id)]["money"] += money
            game_data["players"][str(player_id)][
                "achievements"
            ].append(
                f"День {number_of_day}. Помощь в голосовании за "
                f"{aim_data['url']} ({aim_data['pretty_role']}) - {money}{MONEY_SYM}"
            )

    def cancel_actions(self, game_data: GameCache, user_id: int):
        game_data[self.extra_data[0].key].clear()
        super().cancel_actions(game_data=game_data, user_id=user_id)
