from aiogram.types import InlineKeyboardButton

from cache.cache_types import (
    ExtraCache,
    GameCache,
    UserIdInt,
    RolesLiteral,
    CheckedForTheSameGroups,
)
from keyboards.inline.keypads.mailing import selection_to_warden_kb
from services.game.roles.base import ActiveRoleAtNight
from services.game.roles.base.mixins import ProcedureAfterNight
from states.states import UserFsm
from utils.informing import remind_worden_about_inspections


class Warden(ProcedureAfterNight, ActiveRoleAtNight):
    role = "Соглядатай"
    photo = (
        "https://cdn1.tenchat.ru/static"
        "/vbc-gostinder/2024-08-03/2aa74472-db98-47ac-a427-b3f7dbb020cb.jpeg?"
        "width=2094&height=2094&fmt=webp"
    )
    need_to_monitor_interaction = False
    need_to_process = False
    purpose = "Ты можешь проверить двух любых игроков на принадлежность одной группировки."
    message_to_group_after_action = "Осуществляется плановая проверка документов отдельных социальных структур!"
    mail_message = "Выбери 2х игроков для проверки"
    extra_data = [
        ExtraCache(key="checked_for_the_same_groups"),
        ExtraCache(
            key="text_about_checked_for_the_same_groups",
            is_cleared=False,
            data_type=str,
        ),
    ]
    notification_message = (
        "Кто-то взаимодействовал с твоими документами"
    )
    payment_for_treatment = 15
    payment_for_murder = 16

    def __init__(self):
        self.state_for_waiting_for_action = (
            UserFsm.SUPERVISOR_COLLECTS_INFORMATION
        )
        self.was_deceived: bool = False

    def _get_user_roles_and_url(
        self,
        game_data: GameCache,
        checked_users: CheckedForTheSameGroups,
    ):
        user1_data, user2_data = checked_users
        user1_id, user1_role_key = user1_data
        user2_id, user2_role_key = user2_data
        user1_role = self.all_roles[user1_role_key]
        user2_role = self.all_roles[user2_role_key]
        user_1_url = game_data["players"][str(user1_id)]["url"]
        user_2_url = game_data["players"][str(user2_id)]["url"]
        return user_1_url, user1_role, user_2_url, user2_role

    async def procedure_after_night(
        self, game_data: GameCache, **kwargs
    ):
        checked_users = game_data[self.extra_data[0].key]
        if len(checked_users) != 2:
            return
        user1_url, user1_role, user2_url, user2_role = (
            self._get_user_roles_and_url(
                game_data=game_data, checked_users=checked_users
            )
        )
        common_text = f"🌃Ночь {game_data['number_of_night']}\n{user1_url} и {user2_url} состоят в "
        if user1_role.grouping == user2_role.grouping:
            common_text += "одной группировке!"
        else:
            common_text += "разных группировках!"
        for warden_id in game_data[self.roles_key]:
            await self.bot.send_message(
                chat_id=warden_id, text=common_text
            )
        game_data[self.extra_data[1].key] += common_text + "\n\n"

    async def accrual_of_overnight_rewards(
        self,
        game_data: GameCache,
        **kwargs,
    ):
        checked_users = game_data[self.extra_data[0].key]
        if len(checked_users) != 2:
            return
        if self.was_deceived is False:
            user1_url, user1_role, user2_url, user2_role = (
                self._get_user_roles_and_url(
                    game_data=game_data, checked_users=checked_users
                )
            )
            self.add_money_to_all_allies(
                game_data=game_data,
                money=15,
                custom_message=f"Проверка на совпадение групп {user1_url} ({user1_role.role}) и {user2_url} ({user2_role.role})",
            )
        self.was_deceived = False

    def cancel_actions(self, game_data: GameCache, user_id: int):
        game_data[self.extra_data[0].key].clear()
        return super().cancel_actions(
            game_data=game_data, user_id=user_id
        )

    def generate_markup(
        self,
        player_id: int,
        game_data: GameCache,
        extra_buttons: tuple[InlineKeyboardButton, ...] = (),
    ):
        return selection_to_warden_kb(
            game_data=game_data, user_id=player_id
        )

    @staticmethod
    def get_general_text_before_sending(
        game_data: GameCache,
    ) -> str | None:
        return remind_worden_about_inspections(game_data=game_data)
