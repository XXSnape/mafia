from cache.cache_types import ExtraCache, GameCache
from services.roles.base import (
    AliasRole,
    BossIsDeadMixin,
    ActiveRoleAtNight,
)
from cache.roleses import Groupings
from keyboards.inline.keypads.mailing import (
    kill_or_check_on_policeman,
)
from states.states import UserFsm
from utils.validators import remind_commissioner_about_inspections


class PolicemanAlias(AliasRole):
    role = "Генерал"
    photo = "https://img.clipart-library.com/2/clip-monsters-vs-aliens/clip-monsters-vs-aliens-21.gif"

    purpose = "Ты правая рука маршала. В случае его смерти вступишь в должность."

    def __init__(self):
        self.state_for_waiting_for_action = UserFsm.POLICEMAN_CHECKS

    @classmethod
    @property
    def roles_key(cls):
        return Policeman.roles_key

    @classmethod
    @property
    def processed_users_key(cls):
        return Policeman.processed_users_key


class Policeman(BossIsDeadMixin, ActiveRoleAtNight):
    role = "Маршал. Верховный главнокомандующий армии"
    photo = "https://avatars.mds.yandex.net/get-kinopoisk-image/1777765/59ba5e74-7a28-47b2-944a-2788dcd7ebaa/1920x"
    grouping = Groupings.civilians
    need_to_monitor_interaction = False
    purpose = "Тебе нужно вычислить мафию или уничтожить её. Только ты можешь принимать решения."
    message_to_group_after_action = (
        "В город введены войска! Идет перестрелка!"
    )
    message_to_user_after_action = "Ты выбрал убить {url}"
    mail_message = "Какие меры примешь для ликвидации мафии?"
    can_kill_at_night = True
    alias = PolicemanAlias()
    extra_data = [
        ExtraCache(key="disclosed_roles"),
        ExtraCache(
            key="text_about_checks",
            is_cleared=False,
            data_type=str,
        ),
    ]

    def __init__(self):
        self.state_for_waiting_for_action = UserFsm.POLICEMAN_CHECKS

    async def send_delayed_messages_after_night(
        self, game_data: GameCache
    ):
        if game_data["disclosed_roles"]:
            user_id, role = game_data["disclosed_roles"][0]
            if game_data.get("forged_roles"):
                faked_id, faked_role = game_data["forged_roles"][0]
                if faked_id == user_id:
                    role = faked_role
            url = game_data["players"][str(user_id)]["url"]
            text = f"{url} - {role}!"
            for policeman_id in game_data[self.roles_key]:
                await self.bot.send_message(
                    chat_id=policeman_id, text=text
                )
            game_data["text_about_checks"] += text + "\n"
            await self.state.set_data(game_data)

    async def mailing(self, game_data: GameCache):
        if self.processed_users_key not in game_data:
            return
        policeman = game_data[self.roles_key]
        if not policeman:
            return
        for policeman_id in policeman:
            await self.bot.send_message(
                chat_id=policeman_id,
                text=remind_commissioner_about_inspections(
                    game_data=game_data
                ),
            )
        sent_survey = await self.bot.send_message(
            chat_id=policeman[0],
            text=self.mail_message,
            reply_markup=kill_or_check_on_policeman(),
        )
        await self.save_msg_to_delete_and_change_state(
            game_data=game_data,
            player_id=policeman[0],
            message_id=sent_survey.message_id,
        )
