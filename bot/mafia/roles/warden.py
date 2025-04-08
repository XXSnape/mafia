from aiogram.types import InlineKeyboardButton

from cache.cache_types import (
    ExtraCache,
    GameCache,
    DisclosedRoles,
)
from general.text import ROLE_IS_KNOWN
from keyboards.inline.keypads.mailing import selection_to_warden_kb
from mafia.roles.base import ActiveRoleAtNightABC
from mafia.roles.base.mixins import ProcedureAfterNightABC
from mafia.roles.descriptions.description import RoleDescription
from states.states import UserFsm
from utils.informing import (
    remind_worden_about_inspections,
    send_a_lot_of_messages_safely,
)
from utils.pretty_text import make_pretty


class Warden(ProcedureAfterNightABC, ActiveRoleAtNightABC):
    role = "Соглядатай"
    role_id = "warden"
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
            need_to_clear=False,
            data_type=str,
        ),
    ]
    notification_message = ROLE_IS_KNOWN
    number_in_order_after_night = 2
    payment_for_treatment = 15
    payment_for_murder = 16

    @property
    def role_description(self) -> RoleDescription:
        return RoleDescription(
            skill="Проверяет 2ух игроков на факт принадлежности одной группировки",
            pay_for=["Проверку игроков"],
        )

    def __init__(self):
        self.state_for_waiting_for_action = (
            UserFsm.SUPERVISOR_COLLECTS_INFORMATION
        )
        self.temporary_roles = {}

    def _get_user_roles_and_url(
        self,
        game_data: GameCache,
        checked_users: DisclosedRoles,
        use_temporary_roles: bool = True,
    ):

        user1_id, user2_id = checked_users
        if use_temporary_roles:
            user1_role_id = self.temporary_roles.get(
                user1_id,
                game_data["players"][str(user1_id)]["role_id"],
            )
            user2_role_id = self.temporary_roles.get(
                user2_id,
                game_data["players"][str(user2_id)]["role_id"],
            )
        else:
            user1_role_id = game_data["players"][str(user1_id)][
                "role_id"
            ]
            user2_role_id = game_data["players"][str(user2_id)][
                "role_id"
            ]
        user1_role = self.all_roles[user1_role_id]
        user2_role = self.all_roles[user2_role_id]
        user1_url = game_data["players"][str(user1_id)]["url"]
        user2_url = game_data["players"][str(user2_id)]["url"]
        return user1_url, user1_role, user2_url, user2_role

    async def procedure_after_night(
        self, game_data: GameCache, **kwargs
    ):
        checked_users = game_data["checked_for_the_same_groups"]
        if len(checked_users) != 2:
            return
        user1_url, user1_role, user2_url, user2_role = (
            self._get_user_roles_and_url(
                game_data=game_data, checked_users=checked_users
            )
        )
        common_text = f"🌃Ночь {game_data['number_of_night']}\n{user1_url} и {user2_url} состоят в "
        if user1_role.grouping == user2_role.grouping:
            common_text += "одной группировке!✅"
        else:
            common_text += "разных группировках!🚫"
        await send_a_lot_of_messages_safely(
            bot=self.bot,
            users=game_data[self.roles_key],
            text=common_text,
        )
        game_data["text_about_checked_for_the_same_groups"] += (
            common_text + "\n\n"
        )

    async def accrual_of_overnight_rewards(
        self,
        game_data: GameCache,
        **kwargs,
    ):
        checked_users = game_data["checked_for_the_same_groups"]
        if len(checked_users) != 2:
            return
        user1_url, user1_role, user2_url, user2_role = (
            self._get_user_roles_and_url(
                game_data=game_data,
                checked_users=checked_users,
                use_temporary_roles=False,
            )
        )
        self.add_money_to_all_allies(
            game_data=game_data,
            money=9,
            custom_message=f"Проверка на совпадение групп {user1_url} "
            f"({make_pretty(user1_role.role)}) и "
            f"{user2_url} ({make_pretty(user2_role.role)})",
        )

    def leave_notification_message(
        self,
        game_data: GameCache,
    ):
        users = game_data["checked_for_the_same_groups"]
        if len(users) != 2:
            return
        for user_id in users:
            game_data["messages_after_night"].append(
                [user_id, ROLE_IS_KNOWN]
            )

    def cancel_actions(self, game_data: GameCache, user_id: int):
        game_data["checked_for_the_same_groups"].clear()
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

    def get_general_text_before_sending(
        self,
        game_data: GameCache,
    ) -> str | None:
        return remind_worden_about_inspections(game_data=game_data)
