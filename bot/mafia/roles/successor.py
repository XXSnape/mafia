from aiogram.exceptions import TelegramAPIError
from aiogram.types import InlineKeyboardButton
from exceptiongroup import suppress

from cache.cache_types import RolesLiteral, GameCache, UserIdInt
from general.groupings import Groupings
from keyboards.inline.buttons.common import REFUSE_MOVE_BTN
from mafia.roles import ActiveRoleAtNightABC, RoleABC
from mafia.roles.base.mixins import (
    ObligatoryKillerABC,
    FinisherOfNight,
)
from mafia.roles.descriptions.description import RoleDescription
from mafia.roles.descriptions.texts import PAYMENT_FOR_NIGHTS
from states.game import UserFsm
from utils.informing import notify_aliases_about_transformation
from utils.pretty_text import make_build
from utils.roles import (
    change_role,
    get_user_role_and_url,
)
from utils.state import get_state_and_assign


class Successor(
    FinisherOfNight, ObligatoryKillerABC, ActiveRoleAtNightABC
):
    role = "Тенепреемник"
    role_id: RolesLiteral = "successor"
    mail_message = "Если хочешь, можешь убить и получить роль жертвы"
    need_to_monitor_interaction = False
    photo = "https://i.pinimg.com/originals/1b/9f/c7/1b9fc7e4079c3835ab95c64fb46928f4.png"
    purpose = "Ты обычный мирный, но если тебе надоест, убей кого-нибудь и получи другую роль"
    grouping = Groupings.civilians
    message_to_user_after_action = "Ты выбрал убить и получить роль {url}, если тот выживет после голосования"
    message_to_group_after_action = (
        "Некачественное выполнение обязанностей ведёт к насильственной смене власти! "
        "Радикальные структуры уже рвутся устроить революцию!"
    )
    payment_for_treatment = 4
    payment_for_murder = 11
    payment_for_night_spent = 8
    notification_message = None

    def generate_markup(
        self,
        player_id: UserIdInt,
        game_data: GameCache,
        extra_buttons: tuple[InlineKeyboardButton, ...] = (),
    ):
        extra_buttons = (REFUSE_MOVE_BTN,)
        return super().generate_markup(
            player_id=player_id,
            game_data=game_data,
            extra_buttons=extra_buttons,
        )

    @property
    def role_description(self) -> RoleDescription:
        from .poisoner import Poisoner
        from .analyst import Analyst

        return RoleDescription(
            skill="Может убить любого игрока и получить его роль, если он не умрёт раньше: после ночи или голосования. "
            "Потом фактически доигрывает за него. "
            f"Если роль погибшего игрока побеждает в зависимости от прогресса, "
            f"({Poisoner.pretty_role}, {Analyst.pretty_role}), "
            f"то он не сбрасывается и продолжает расти у погибшего.",
            pay_for=[PAYMENT_FOR_NIGHTS],
            features=[
                "Если погибший игрок, например Доктор, выбрал прошлой ночью вылечить игрока А, "
                "то после смены ролей Тенепреемник (новый врач) также сможет вылечить игрока А",
                "Убийство происходит гарантированно после голосования",
            ],
            limitations=[
                "Может убивать и менять роль только после 1-ой ночи",
                "Если умирает до окончания голосования, действия отменяются",
            ],
        )

    def __init__(self):
        self.state_for_waiting_for_action = (
            UserFsm.HEIR_CHOOSES_TARGET
        )
        self.new_role: RoleABC | None = None
        self.user_id: UserIdInt | None = None

    def kill_after_all_actions(
        self,
        game_data: GameCache,
        current_inactive_users: list[UserIdInt],
    ) -> tuple[UserIdInt, str] | None:
        if not game_data[self.roles_key]:
            return None
        processed_user_id = self.get_processed_user_id(game_data)
        if processed_user_id is None:
            return None
        if processed_user_id not in game_data["live_players_ids"]:
            return None
        processed_role, user_url = get_user_role_and_url(
            game_data=game_data,
            processed_user_id=processed_user_id,
            all_roles=self.all_roles,
        )
        self.new_role = processed_role
        self.user_id = game_data[self.roles_key][0]
        change_role(
            game_data=game_data,
            previous_role=self,
            new_role=self.new_role,
            user_id=game_data[self.roles_key][0],
        )
        return (
            processed_user_id,
            "😉На твоё место пришел преемник. Пожелай ему удачи!",
        )

    async def end_night(self, game_data: GameCache):
        if (
            self.new_role is None
            or self.user_id not in game_data["live_players_ids"]
        ):
            return
        updated_new_role = self.all_roles[
            game_data["players"][str(self.user_id)]["role_id"]
        ]

        if updated_new_role.state_for_waiting_for_action:
            await get_state_and_assign(
                dispatcher=self.dispatcher,
                chat_id=self.user_id,
                bot_id=self.bot.id,
                new_state=updated_new_role.state_for_waiting_for_action,
            )
        with suppress(TelegramAPIError):
            await self.bot.send_photo(
                chat_id=self.user_id,
                photo=updated_new_role.photo,
                caption=make_build(
                    f"❗️Отныне твоя новая роль — {updated_new_role.pretty_role}"
                ),
            )

        if (updated_new_role.grouping == Groupings.criminals) or (
            (updated_new_role.alias or updated_new_role.is_alias)
            and game_data["settings"]["show_peaceful_allies"]
        ):
            await notify_aliases_about_transformation(
                game_data=game_data,
                bot=self.bot,
                new_role=updated_new_role,
                user_id=self.user_id,
                exclude_user=True,
            )
