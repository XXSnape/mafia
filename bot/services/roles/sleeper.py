from cache.cache_types import ExtraCache, GameCache
from services.roles.base.roles import Groupings
from services.roles.base import ActiveRoleAtNight, Role
from services.roles.base.mixins import ProcedureAfterNight
from states.states import UserFsm
from utils.validators import get_processed_user_id_if_exists


class Sleeper(ProcedureAfterNight, ActiveRoleAtNight):
    role = "Клофелинщица"
    mail_message = "Кого усыпить этой ночью?"
    photo = (
        "https://masterpiecer-images.s3.yandex.net/c94e9c"
        "b6787b11eeb1ce1e5d9776cfa6:upscaled"
    )
    grouping = Groupings.civilians
    purpose = "Ты можешь усыпить кого-нибудь"
    message_to_group_after_action = "Спят взрослые и дети. Не обошлось и без помощи клофелинщиков!"
    message_to_user_after_action = "Ты выбрал усыпить {url}"
    extra_data = [
        ExtraCache(key="tracking", data_type=dict),
    ]
    number_in_order = 0
    payment_for_treatment = 8
    payment_for_murder = 8

    def __init__(self):
        self.state_for_waiting_for_action = (
            UserFsm.CLOFFELINE_GIRL_PUTS_TO_SLEEP
        )

    @get_processed_user_id_if_exists
    async def procedure_after_night(
        self,
        all_roles: dict[str, Role],
        game_data: GameCache,
        processed_user_id: int,
    ):
        user_role = game_data["players"][str(processed_user_id)][
            "enum_name"
        ]
        role: Role = all_roles[user_role]
        is_active_role = False
        if isinstance(role, ActiveRoleAtNight) is False:
            money = 0
        else:
            money = role.payment_for_murder
            is_active_role = True
        for sleeper_id in game_data[self.roles_key]:
            url = game_data["players"][str(processed_user_id)]["url"]
            user_role = game_data["players"][str(sleeper_id)]["url"]
            game_data["players"][str(sleeper_id)]["money"] += money
            game_data["players"][str(sleeper_id)][
                "achievements"
            ].append(
                f'Ночь {game_data["number_of_night"]}. '
                f"Усыпление {url} ({user_role}) - {money}💵"
            )

        if not is_active_role:
            return
        send_message = role.cancel_actions(
            game_data=game_data, user_id=processed_user_id
        )
        if send_message:
            await self.bot.send_message(
                chat_id=processed_user_id,
                text="Сложно поверить, но все твои действия ночью были лишь сном!",
            )
