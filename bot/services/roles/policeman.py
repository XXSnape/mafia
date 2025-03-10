from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from cache.cache_types import ExtraCache, GameCache
from cache.roleses import Groupings
from keyboards.inline.keypads.mailing import (
    kill_or_check_on_policeman,
)
from services.roles.base import (
    ActiveRoleAtNight,
    AliasRole,
    BossIsDeadMixin,
)
from services.roles.base.mixins import ProcedureAfterNight
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

    @classmethod
    @property
    def last_interactive_key(cls):
        return Policeman.last_interactive_key


class Policeman(
    ProcedureAfterNight, BossIsDeadMixin, ActiveRoleAtNight
):
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
    number_in_order = 2

    def __init__(self):
        self.state_for_waiting_for_action = UserFsm.POLICEMAN_CHECKS

    async def procedure_after_night(
        self, game_data: GameCache, murdered: list[int]
    ):
        if game_data["disclosed_roles"]:
            user_id, role = game_data["disclosed_roles"][0]
            url = game_data["players"][str(user_id)]["url"]
            text = f"{url} - {role}!"
            for policeman_id in game_data[self.roles_key]:
                await self.bot.send_message(
                    chat_id=policeman_id, text=text
                )
            game_data["text_about_checks"] += text + "\n"
            await self.state.set_data(game_data)
        else:
            processed_user_id = self.get_processed_user_id(game_data)
            if processed_user_id:
                murdered.append(processed_user_id)

    def cancel_actions(self, game_data: GameCache, user_id: int):
        if game_data["disclosed_roles"]:
            game_data["disclosed_roles"].clear()
            return True
        return super().cancel_actions(
            game_data=game_data, user_id=user_id
        )

    # async def send_delayed_messages_after_night(
    #     self, game_data: GameCache
    # ):
    #     if game_data["disclosed_roles"]:
    #         user_id, role = game_data["disclosed_roles"][0]
    #         if game_data.get("forged_roles"):
    #             faked_id, faked_role = game_data["forged_roles"][0]
    #             if faked_id == user_id:
    #                 role = faked_role
    #         url = game_data["players"][str(user_id)]["url"]
    #         text = f"{url} - {role}!"
    #         for policeman_id in game_data[self.roles_key]:
    #             await self.bot.send_message(
    #                 chat_id=policeman_id, text=text
    #             )
    #         game_data["text_about_checks"] += text + "\n"
    #         await self.state.set_data(game_data)

    def generate_markup(
        self,
        player_id: int,
        game_data: GameCache,
        extra_buttons: tuple[InlineKeyboardButton, ...] = (),
    ):
        return kill_or_check_on_policeman()

    async def mailing(
        self,
        game_data: GameCache,
        own_markup: InlineKeyboardMarkup | None = None,
    ):
        policeman = self.get_roles(game_data)
        if not policeman:
            return
        for policeman_id in policeman:
            await self.bot.send_message(
                chat_id=policeman_id,
                text=remind_commissioner_about_inspections(
                    game_data=game_data
                ),
            )
        await super().mailing(game_data=game_data)
