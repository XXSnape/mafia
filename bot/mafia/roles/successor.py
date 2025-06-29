from aiogram.exceptions import TelegramAPIError
from cache.cache_types import GameCache, RolesLiteral, UserIdInt
from exceptiongroup import suppress
from general.groupings import Groupings
from mafia.roles import ActiveRoleAtNightABC, RoleABC
from mafia.roles.base.mixins import (
    FinisherOfNight,
    SunsetKillerABC,
)
from mafia.roles.descriptions.description import RoleDescription
from mafia.roles.descriptions.texts import (
    MAY_SKIP_MOVE,
    PAYMENT_FOR_NIGHTS,
)
from utils.informing import notify_aliases_about_transformation
from utils.pretty_text import make_build
from utils.roles import (
    change_role,
    get_user_role_and_url,
)
from utils.state import get_state_and_assign


class Successor(
    FinisherOfNight,
    SunsetKillerABC,
    ActiveRoleAtNightABC,
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
    is_possible_to_skip_move = True
    number_in_order_after_sunset: int = 3

    @staticmethod
    def allow_sending_mailing(game_data: GameCache) -> bool:
        return game_data["number_of_night"] > 1

    @property
    def role_description(self) -> RoleDescription:
        from .analyst import Analyst
        from .bride import Bride
        from .poisoner import Poisoner

        return RoleDescription(
            skill="Может убить любого игрока и получить его роль, "
            "если он не умрёт раньше: после ночи, или голосования, или из-за неактивности. "
            "Потом фактически доигрывает за него. "
            f"Если роль погибшего игрока побеждает в зависимости от прогресса, "
            f"({Poisoner.pretty_role}, {Analyst.pretty_role}, {Bride.pretty_role}), "
            f"то он не сбрасывается и продолжает расти у погибшего.",
            pay_for=[PAYMENT_FOR_NIGHTS],
            features=[MAY_SKIP_MOVE],
            limitations=[
                "Может убивать и менять роль только после 1-ой ночи",
                "Если умирает до наступления следующей ночи, действия отменяются",
                "Не может убить того, кто был излечен врачом или другим персонажем",
            ],
        )

    def __init__(self):
        super().__init__()
        self.new_role: RoleABC | None = None
        self.user_id: UserIdInt | None = None

    def kill_after_all_actions(
        self,
        game_data: GameCache,
        current_inactive_users: list[UserIdInt],
        cured_users: list[UserIdInt],
    ) -> tuple[UserIdInt, str] | None:
        if not game_data[self.roles_key]:
            return None
        processed_user_id = self.get_processed_user_id(game_data)
        if processed_user_id is None:
            return None
        if (
            processed_user_id not in game_data["live_players_ids"]
            or processed_user_id in cured_users
        ):
            return None
        processed_role, user_url = get_user_role_and_url(
            game_data=game_data,
            processed_user_id=processed_user_id,
            all_roles=self.all_roles,
        )
        if processed_role.alias:
            self.new_role = processed_role.alias
        else:
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
        from .bride import Bride

        if (
            self.new_role is None
            or self.user_id not in game_data["live_players_ids"]
        ):
            return
        self.new_role = None
        updated_new_role = self.all_roles[
            game_data["players"][str(self.user_id)]["role_id"]
        ]
        if isinstance(updated_new_role, ActiveRoleAtNightABC):
            await get_state_and_assign(
                dispatcher=self.dispatcher,
                chat_id=self.user_id,
                bot_id=self.bot.id,
                new_state=updated_new_role.state_for_waiting_for_action,
            )
        with suppress(TelegramAPIError):
            message = f"❗️Отныне твоя новая роль — {updated_new_role.pretty_role}"
            if isinstance(updated_new_role, Bride):
                groom_id = self.all_roles[Bride.role_id].groom_id
                url = game_data["players"][str(groom_id)]["url"]
                message += f"\n\nТвой муж — {url}"
            await self.bot.send_photo(
                chat_id=self.user_id,
                photo=updated_new_role.photo,
                caption=make_build(message),
                protect_content=game_data["settings"][
                    "protect_content"
                ],
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
