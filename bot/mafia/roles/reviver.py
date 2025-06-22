from contextlib import suppress

from aiogram.exceptions import TelegramAPIError
from cache.cache_types import GameCache, RolesLiteral, UserIdInt
from general.groupings import Groupings
from mafia.roles import ActiveRoleAtNightABC
from mafia.roles.base.mixins import (
    FinisherOfNight,
    ProcedureAfterVotingABC,
)
from mafia.roles.descriptions.description import RoleDescription
from utils.roles import (
    change_role,
    get_processed_user_id_if_exists,
    get_user_role_and_url,
)


class Reviver(
    FinisherOfNight,
    ProcedureAfterVotingABC,
    ActiveRoleAtNightABC,
):
    # врача и маршала не заменять
    role = "Воскреситель"
    role_id: RolesLiteral = "reviver"
    grouping = Groupings.civilians
    purpose = (
        f"Если погибнут все маршалы или врачи, "
        f"сможешь выбрать любого игрока, "
        f"и, если его группировка {Groupings.civilians.name}, "
        f"он станет маршалом или врачом"
    )
    message_to_group_after_action = None
    photo = (
        "https://media.2x2tv.ru/content"
        "/images/size/w1440h1080/2024/03/megamiiiiiindtwocoveeeer.jpg"
    )
    mail_message = "Кого попытаешься превратить в маршала или врача?"
    message_to_user_after_action = (
        "Ты выбрал превратить {url} в маршала или врача"
    )
    need_to_monitor_interaction = False
    payment_for_treatment = 12
    payment_for_murder = 14

    @property
    def role_description(self) -> RoleDescription:
        return RoleDescription(
            skill="Если в игре не осталось маршала или врача, "
            "тогда выбирает их заместителя. Если после ночи и голосования "
            "заместитель остается жив, то он становится маршалом или доктором.",
            pay_for=["Перевоплощения в маршала или доктора"],
            limitations=[
                f"Можно перевоплощать только членов группировки {Groupings.civilians.value.name}",
                "Если выбранная цель является врачом, или маршалом, или их союзником, "
                "её перевоплотить нельзя. "
                "Другими словами, если в игре нет маршала, доктор не сможет занять его место, и наоборот",
            ],
            features=[
                "В случае, если в игре нет ни маршалов, ни докторов, выбранный заместитель превращается в маршала"
            ],
        )

    def __init__(self):
        super().__init__()
        self.reborn_id: UserIdInt | None = None

    @get_processed_user_id_if_exists
    async def take_action_after_voting(
        self,
        game_data: GameCache,
        processed_user_id: UserIdInt,
        **kwargs,
    ):
        self.reborn_id = processed_user_id

    @staticmethod
    def allow_sending_mailing(game_data: GameCache) -> bool:
        from .doctor import Doctor
        from .policeman import Policeman

        return (not game_data[Policeman.roles_key]) or (
            not game_data[Doctor.roles_key]
        )

    async def end_night(self, game_data: GameCache):
        from .doctor import Doctor
        from .policeman import Policeman

        user_id = self.reborn_id
        self.reborn_id = None
        if (
            user_id is None
            or user_id not in game_data["live_players_ids"]
        ):
            return

        current_role, url = get_user_role_and_url(
            game_data=game_data,
            processed_user_id=user_id,
            all_roles=self.all_roles,
        )
        if (
            current_role.grouping != Groupings.civilians
            or current_role.role_id
            in (Policeman.role_id, Doctor.role_id)
        ):
            return
        if not game_data[Policeman.roles_key]:
            new_role = Policeman()
        elif not game_data[Doctor.roles_key]:
            new_role = Doctor()
        else:
            return
        change_role(
            game_data=game_data,
            previous_role=current_role,
            new_role=new_role,
            user_id=user_id,
        )
        self.add_money_to_all_allies(
            game_data=game_data,
            money=30,
            user_url=url,
            custom_message=f"Перевоплощение {url} "
            f"({current_role.pretty_role}) в ({new_role.pretty_role})",
            at_night=None,
        )
        with suppress(TelegramAPIError):
            await self.bot.send_photo(
                chat_id=user_id,
                photo=new_role.photo,
                caption=f"Ты снят с предыдущей должности, и "
                f"теперь твоя роль — {new_role.pretty_role}.\n\n"
                f"Выполняй свои обязанности достойно🫡",
                protect_content=game_data["settings"][
                    "protect_content"
                ],
            )
