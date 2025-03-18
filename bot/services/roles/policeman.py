from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from cache.cache_types import ExtraCache, GameCache
from services.roles.base.roles import Groupings, Role
from constants.output import ROLE_IS_KNOWN
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
from utils.validators import (
    remind_commissioner_about_inspections,
    get_processed_role_and_user_if_exists,
    get_user_role_and_url,
)


class Policeman(
    ProcedureAfterNight, BossIsDeadMixin, ActiveRoleAtNight
):
    role = "Маршал. Верховный главнокомандующий армии"
    photo = "https://avatars.mds.yandex.net/get-kinopoisk-image/1777765/59ba5e74-7a28-47b2-944a-2788dcd7ebaa/1920x"
    need_to_monitor_interaction = False
    purpose = "Тебе нужно вычислить мафию или уничтожить её. Только ты можешь принимать решения."
    message_to_group_after_action = (
        "В город введены войска! Идет перестрелка!"
    )
    message_to_user_after_action = "Ты выбрал убить {url}"
    mail_message = "Какие меры примешь для ликвидации мафии?"
    can_kill_at_night = True
    extra_data = [
        ExtraCache(key="disclosed_roles"),
        ExtraCache(
            key="text_about_checks",
            is_cleared=False,
            data_type=str,
        ),
    ]
    number_in_order_after_night = 2
    notification_message = None
    payment_for_treatment = 18
    payment_for_murder = 20

    def __init__(self):
        self.state_for_waiting_for_action = UserFsm.POLICEMAN_CHECKS

    async def accrual_of_overnight_rewards(
        self,
        all_roles: dict[str, Role],
        game_data: GameCache,
        victims: set[int],
        **kwargs,
    ):
        disclosed_roles = game_data["disclosed_roles"]
        if (
            disclosed_roles
            and disclosed_roles != game_data["forged_roles"]
        ):
            processed_role, user_url = get_user_role_and_url(
                game_data=game_data,
                processed_user_id=disclosed_roles[0][0],
                all_roles=all_roles,
            )
            self.add_money_to_all_allies(
                game_data=game_data,
                money=9,
                user_url=user_url,
                processed_role=processed_role,
                beginning_message="Проверка",
            )
            return
        processed_user_id = self.get_processed_user_id(game_data)
        if (
            processed_user_id is None
            or processed_user_id not in victims
        ):
            return
        processed_role, user_url = get_user_role_and_url(
            game_data=game_data,
            processed_user_id=processed_user_id,
            all_roles=all_roles,
        )
        money = (
            0
            if processed_role.grouping == Groupings.civilians
            else processed_role.payment_for_murder
        )
        self.add_money_to_all_allies(
            game_data=game_data,
            money=money,
            user_url=user_url,
            processed_role=processed_role,
            beginning_message="Убийство",
        )

    async def procedure_after_night(
        self, game_data: GameCache, murdered: list[int], **kwargs
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
            game_data["messages_after_night"].remove(
                [game_data["disclosed_roles"][0][0], ROLE_IS_KNOWN]
            )
            game_data["disclosed_roles"].clear()
            return True
        return super().cancel_actions(
            game_data=game_data, user_id=user_id
        )

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


class PolicemanAlias(AliasRole, Policeman):
    role = "Генерал"
    photo = "https://img.clipart-library.com/2/clip-monsters-vs-aliens/clip-monsters-vs-aliens-21.gif"
    payment_for_treatment = 11
    payment_for_murder = 14
    purpose = "Ты правая рука маршала. В случае его смерти вступишь в должность."
