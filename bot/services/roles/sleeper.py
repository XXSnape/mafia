from cache.cache_types import ExtraCache, GameCache
from cache.roleses import Groupings
from general.collection_of_roles import Roles
from services.roles import Forger, Policeman
from services.roles.base import ActiveRoleAtNight, Role
from states.states import UserFsm
from utils.validators import get_object_id_if_exists


class Sleeper(ActiveRoleAtNight):
    role = "Клофелинщица"
    mail_message = "Кого усыпить этой ночью?"
    photo = (
        "https://masterpiecer-images.s3.yandex.net/c94e9c"
        "b6787b11eeb1ce1e5d9776cfa6:upscaled"
    )
    grouping = Groupings.criminals
    purpose = "Ты можешь усыпить кого-нибудь во имя мафии."
    message_to_group_after_action = "Спят взрослые и дети. Не обошлось и без помощи клофелинщиков!"
    message_to_user_after_action = "Ты выбрал усыпить {url}"
    extra_data = [
        ExtraCache(key="tracking", data_type=dict),
    ]

    def __init__(self):
        self.state_for_waiting_for_action = (
            UserFsm.CLOFFELINE_GIRL_PUTS_TO_SLEEP
        )

    @get_object_id_if_exists
    async def earliest_actions_after_night(self, user_id: int):
        game_data: GameCache = await self.state.get_data()
        euthanized_user_id = user_id
        user_role = game_data["players"][str(euthanized_user_id)][
            "role"
        ]
        send_message = False
        for role in Roles:
            current_role: Role = role.value
            if (
                current_role.role == Policeman.role
                and game_data["disclosed_roles"]
            ):
                game_data["disclosed_roles"].clear()
                break
            if current_role.role == Forger.role:
                game_data["forged_roles"].clear()
                break
            if current_role.role != user_role:
                continue
            suffers = (
                game_data["tracking"]
                .get(str(euthanized_user_id), {})
                .get("sufferers", [])
            )
            for suffer in suffers:
                if current_role.processed_users_key:
                    send_message = True
                    game_data[
                        current_role.processed_users_key
                    ].remove(suffer)
            break
        if send_message:
            await self.bot.send_message(
                chat_id=euthanized_user_id,
                text="Сложно поверить, но все твои действия ночью были лишь сном!",
            )
