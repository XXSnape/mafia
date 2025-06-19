import asyncio

from cache.cache_types import (
    GameCache,
    RolesLiteral,
    UserIdInt,
    PlayersIds,
)
from cache.extra import ExtraCache
from general.groupings import Groupings
from mafia.roles.base import ActiveRoleAtNightABC
from mafia.roles.base.mixins import (
    FinisherOfNight,
    ProcedureAfterVotingABC,
    ProcedureAfterNightABC,
)
from mafia.roles.base.roles import RoleABC
from mafia.roles.descriptions.description import RoleDescription
from mafia.roles.descriptions.texts import (
    PAYMENT_FOR_NIGHTS,
    SAVING_PLAYER,
)
from states.game import UserFsm
from utils.pretty_text import make_build
from utils.roles import (
    get_processed_role_and_user_if_exists,
    get_processed_user_id_if_exists,
)
from utils.state import reset_user_state


class AngelOfDeath(
    FinisherOfNight,
    ProcedureAfterVotingABC,
    ProcedureAfterNightABC,
    ActiveRoleAtNightABC,
):
    role = "Ангел-Хранитель"
    role_id: RolesLiteral = "angel_of_death"
    mail_message = "Ты здесь, чтобы помочь человечеству исправить ошибки! Кого ты излечишь?"
    need_to_monitor_interaction = False
    photo = "https://avatars.mds.yandex.net/get-entity_search/10844899/935958285/S600xU_2x"
    purpose = "Если ты умрешь на голосовании, сможешь следующей ночью кого-нибудь вылечить"
    grouping = Groupings.civilians
    extra_data = [ExtraCache(key="angels_died", need_to_clear=False)]
    message_to_user_after_action = "Ты выбрал спасти {url}"
    message_to_group_after_action = (
        "Во имя добра пойдешь и не думаешь о мести..."
    )
    payment_for_night_spent = 7
    clearing_state_after_death = False
    number_in_order_after_voting = 3

    @property
    def role_description(self) -> RoleDescription:
        return RoleDescription(
            skill="Может вылечить любого, если его убьют днём",
            pay_for=[SAVING_PLAYER, PAYMENT_FOR_NIGHTS],
        )

    async def take_action_after_voting(
        self,
        game_data: GameCache,
        removed_user: list[UserIdInt],
        **kwargs,
    ):
        removed_user_id = removed_user[0]
        if removed_user_id in game_data.get(self.roles_key, []):
            game_data["angels_died"].append(removed_user_id)

    @get_processed_user_id_if_exists
    async def procedure_after_night(
        self,
        game_data: GameCache,
        processed_user_id: UserIdInt,
        recovered: PlayersIds,
        **kwargs,
    ):
        recovered.append(processed_user_id)

    @get_processed_role_and_user_if_exists
    async def accrual_of_overnight_rewards(
        self,
        game_data: GameCache,
        murdered: PlayersIds,
        processed_role: RoleABC,
        user_url: str,
        processed_user_id: UserIdInt,
        **kwargs,
    ):
        if processed_user_id not in murdered:
            return
        if processed_role.grouping != Groupings.civilians:
            money = 0
        else:
            money = processed_role.payment_for_treatment * 2
        self.add_money_to_all_allies(
            game_data=game_data,
            money=money,
            beginning_message="Добровольное лечение",
            user_url=user_url,
            processed_role=processed_role,
            additional_players=game_data["angels_died"],
        )

    async def end_night(self, game_data: GameCache):
        for angel_id in game_data["angels_died"][:]:
            if (
                game_data["number_of_night"]
                == game_data["players"][str(angel_id)][
                    "number_died_at_night"
                ]
                + 1
            ):
                continue
            game_data["angels_died"].remove(angel_id)
            await reset_user_state(
                dispatcher=self.dispatcher,
                user_id=angel_id,
                bot_id=self.bot.id,
            )

    async def report_death(
        self,
        game_data: GameCache,
        at_night: bool,
        user_id: UserIdInt,
        message_if_died_especially: str | None = None,
    ):
        if at_night is False:
            await self.bot.send_message(
                chat_id=user_id,
                text=make_build(
                    "😢Тебя линчевали на голосовании, но ты не должен мстить, спаси товарищей!"
                ),
                protect_content=game_data["settings"][
                    "protect_content"
                ],
            )
            return
        await super().report_death(
            game_data=game_data,
            at_night=at_night,
            user_id=user_id,
            message_if_died_especially=message_if_died_especially,
        )

    async def mailing(self, game_data: GameCache):
        if not game_data["angels_died"]:
            return
        await asyncio.gather(
            *(
                self.send_survey(
                    player_id=angel_id, game_data=game_data
                )
                for angel_id in game_data["angels_died"][:]
            ),
            return_exceptions=True,
        )

    def __init__(self):
        self.state_for_waiting_for_action = (
            UserFsm.ANGEL_TAKES_REVENGE
        )
