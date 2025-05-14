from aiogram.types import InlineKeyboardButton
from cache.cache_types import GameCache, RolesLiteral, UserIdInt
from general.groupings import Groupings
from general.text import (
    ATTEMPT_TO_KILL,
)
from keyboards.inline.keypads.mailing import (
    send_selection_to_players_kb,
)
from mafia.roles.base import (
    ActiveRoleAtNightABC,
    AliasRoleABC,
)
from mafia.roles.base.mixins import (
    MafiaConverterABC,
    MurderAfterNightABC,
)
from mafia.roles.base.roles import RoleABC
from mafia.roles.descriptions.description import RoleDescription
from mafia.roles.descriptions.texts import (
    CAN_KILL_AT_NIGHT,
    KILLING_PLAYER,
)
from states.game import UserFsm
from utils.common import get_criminals_ids
from utils.roles import (
    change_role,
    get_processed_role_and_user_if_exists,
)


class Mafia(MurderAfterNightABC, ActiveRoleAtNightABC):
    role = "Дон. Высшее звание в преступных группировках"
    role_id: RolesLiteral = "don"
    photo = "https://proza.ru/pics/2021/02/21/523.jpg"
    grouping = Groupings.criminals
    purpose = "Тебе нужно руководить преступниками и убивать мирных."
    message_to_group_after_action = "Мафия выбрала жертву!"
    message_to_user_after_action = "Ты выбрал убить {url}"
    words_to_aliases_and_teammates = "Убить"
    mail_message = "Кого убить этой ночью?"
    need_to_monitor_interaction = False
    notification_message = ATTEMPT_TO_KILL
    payment_for_treatment = 0
    payment_for_murder = 20

    @property
    def role_description(self) -> RoleDescription:
        return RoleDescription(
            skill=CAN_KILL_AT_NIGHT,
            pay_for=[KILLING_PLAYER],
            features=[
                "Жертва выбирается решением большинства союзников. В случае неопределенности решение принимает Дон.",
            ],
        )

    def __init__(self):
        self.state_for_waiting_for_action = UserFsm.MAFIA_ATTACKS

    def _get_players(self, game_data: GameCache):
        mafias = super()._get_players(game_data)
        if mafias:
            return mafias
        criminals = get_criminals_ids(game_data)
        if not criminals:
            return criminals
        user_id = criminals[0]
        for criminal_id in criminals:
            role: MafiaConverterABC = self.all_roles[
                game_data["players"][str(criminal_id)]["role_id"]
            ]
            if isinstance(
                role, MafiaConverterABC
            ) is False or role.check_for_possibility_to_transform(
                game_data
            ):
                change_role(
                    game_data=game_data,
                    previous_role=role,
                    new_role=self,
                    user_id=criminal_id,
                )
                return [criminal_id]
        change_role(
            game_data=game_data,
            previous_role=self.all_roles[
                game_data["players"][str(user_id)]["role_id"]
            ],
            new_role=self,
            user_id=user_id,
        )
        return [user_id]

    def generate_markup(
        self,
        player_id: int,
        game_data: GameCache,
        extra_buttons: tuple[InlineKeyboardButton, ...] = (),
    ):
        if game_data["settings"]["can_kill_teammates"]:
            exclude = [player_id]
        else:
            exclude = get_criminals_ids(game_data)
        return send_selection_to_players_kb(
            players_ids=game_data["live_players_ids"],
            players=game_data["players"],
            exclude=exclude,
            extra_buttons=extra_buttons,
        )

    @get_processed_role_and_user_if_exists
    async def accrual_of_overnight_rewards(
        self,
        game_data: GameCache,
        victims: set[UserIdInt],
        processed_role: RoleABC,
        user_url: str,
        processed_user_id: UserIdInt,
        **kwargs
    ):
        if processed_user_id not in victims:
            return
        money = (
            0
            if processed_role.grouping == Groupings.criminals
            else processed_role.payment_for_murder
        )
        self.add_money_to_all_allies(
            game_data=game_data,
            money=money,
            user_url=user_url,
            processed_role=processed_role,
            beginning_message="Убийство",
        )


class MafiaAlias(AliasRoleABC, Mafia):
    role = "Мафия"
    role_id: RolesLiteral = "mafia"
    photo = (
        "https://steamuserimages-a.akamaihd.net/ugc/253717829589048899/"
        "949E084C8E9DDEA99B969B9CB7B497D86D35D3F1/?imw=512&amp;imh=332&amp;"
        "ima=fit&amp;impolicy=Letterbox&amp;imcolor=%23000000&amp;letterbox=true"
    )
    purpose = (
        "Тебе нужно уничтожить всех горожан и подчиняться дону."
    )
    is_mass_mailing_list = True
    message_to_user_after_action = (
        "Ты выбрал убить {url}. Но Дон может принять другое решение."
    )
    payment_for_treatment = 0
    payment_for_murder = 13
