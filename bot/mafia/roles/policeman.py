from aiogram.types import InlineKeyboardButton
from cache.cache_types import (
    GameCache,
    PlayersIds,
    UserIdInt,
)
from cache.extra import ExtraCache
from general.groupings import Groupings
from general.text import (
    ATTEMPT_TO_KILL,
    ROLE_IS_KNOWN,
)
from keyboards.inline.keypads.mailing import (
    kill_or_check_on_policeman,
)
from mafia.roles.base import (
    ActiveRoleAtNightABC,
    AliasRoleABC,
)
from mafia.roles.base.mixins import KillersOf, ProcedureAfterNightABC
from mafia.roles.descriptions.description import RoleDescription
from mafia.roles.descriptions.texts import (
    CHECKING_PLAYER,
    KILLING_PLAYER,
)
from states.game import UserFsm
from utils.informing import (
    remind_commissioner_about_inspections,
    send_a_lot_of_messages_safely,
)
from utils.pretty_text import make_pretty
from utils.roles import (
    get_user_role_and_url,
)


class Policeman(ProcedureAfterNightABC, ActiveRoleAtNightABC):
    role = "Маршал. Верховный главнокомандующий армии"
    role_id = "policeman"
    photo = "https://avatars.mds.yandex.net/get-kinopoisk-image/1777765/59ba5e74-7a28-47b2-944a-2788dcd7ebaa/1920x"
    need_to_monitor_interaction = False
    purpose = "Тебе нужно вычислить мафию или уничтожить её. Только ты можешь принимать решения."
    message_to_group_after_action = (
        "В город введены войска! Идет перестрелка!"
    )
    message_to_user_after_action = "Ты выбрал расстрелять {url}"
    words_to_aliases_and_teammates = "Расстрелять"
    mail_message = "Какие меры примешь для ликвидации мафии?"
    extra_data = [
        ExtraCache(key="disclosed_roles"),
        ExtraCache(
            key="text_about_checks",
            need_to_clear=False,
            data_type=str,
        ),
    ]
    number_in_order_after_night = 2
    notification_message = ATTEMPT_TO_KILL
    payment_for_treatment = 18
    payment_for_murder = 20

    @property
    def role_description(self) -> RoleDescription:
        return RoleDescription(
            skill="За 1 ночь может либо проверить роль игрока, либо расстрелять его",
            pay_for=[KILLING_PLAYER, CHECKING_PLAYER],
            limitations=[
                "Не может расстрелять в первую ночь",
            ],
        )

    def __init__(self):
        self.state_for_waiting_for_action = UserFsm.POLICEMAN_CHECKS
        self.temporary_roles = {}

    async def accrual_of_overnight_rewards(
        self,
        game_data: GameCache,
        victims: set[UserIdInt],
        **kwargs,
    ):
        disclosed_roles = game_data["disclosed_roles"]
        if game_data["disclosed_roles"]:
            processed_role, user_url = get_user_role_and_url(
                game_data=game_data,
                processed_user_id=disclosed_roles[0],
                all_roles=self.all_roles,
            )
            self.add_money_to_all_allies(
                game_data=game_data,
                money=10,
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
            all_roles=self.all_roles,
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
        self,
        game_data: GameCache,
        murdered: PlayersIds,
        killers_of: KillersOf,
        **kwargs,
    ):

        if game_data["disclosed_roles"]:
            user_id = game_data["disclosed_roles"][0]
            url = game_data["players"][str(user_id)]["url"]
            user_role_id = self.temporary_roles.get(
                user_id,
                game_data["players"][str(user_id)]["role_id"],
            )
            role = self.all_roles[user_role_id].pretty_role
            text = f"🌃Ночь {game_data['number_of_night']}\n{url} - {role}!"
            game_data["text_about_checks"] += text + "\n\n"
            users = (
                game_data[self.roles_key]
                if game_data["settings"]["show_peaceful_allies"]
                else [game_data[self.roles_key][0]]
            )
            await send_a_lot_of_messages_safely(
                bot=self.bot,
                users=users,
                text=text,
            )
        else:
            processed_user_id = self.get_processed_user_id(game_data)
            if processed_user_id:
                killers_of[processed_user_id].append(self)
                murdered.append(processed_user_id)

    def leave_notification_message(
        self,
        game_data: GameCache,
    ):
        if game_data["disclosed_roles"]:
            user_id = game_data["disclosed_roles"][0]
            game_data["messages_after_night"].append(
                [user_id, ROLE_IS_KNOWN]
            )
            return
        return super().leave_notification_message(game_data)

    def cancel_actions(self, game_data: GameCache, user_id: int):
        game_data["disclosed_roles"].clear()
        return super().cancel_actions(
            game_data=game_data, user_id=user_id
        )

    def generate_markup(
        self,
        player_id: int,
        game_data: GameCache,
        extra_buttons: tuple[InlineKeyboardButton, ...] = (),
    ):
        return kill_or_check_on_policeman(game_data=game_data)

    def get_general_text_before_sending(self, game_data: GameCache):
        return remind_commissioner_about_inspections(
            game_data=game_data
        )


class PolicemanAlias(AliasRoleABC, Policeman):
    role = "Генерал"
    role_id = "general"
    photo = "https://img.clipart-library.com/2/clip-monsters-vs-aliens/clip-monsters-vs-aliens-21.gif"
    payment_for_treatment = 11
    payment_for_murder = 14
    purpose = "Ты правая рука маршала. В случае его смерти вступишь в должность."
