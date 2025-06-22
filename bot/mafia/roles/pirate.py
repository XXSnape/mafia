from cache.cache_types import GameCache, RolesLiteral, UserIdInt
from cache.extra import ExtraCache
from general.groupings import Groupings
from mafia.roles.base import ActiveRoleAtNightABC
from mafia.roles.base.mixins import (
    ProcedureAfterVotingABC,
    SpecialMoneyManagerMixin,
    SunsetKillerABC,
)
from mafia.roles.descriptions.description import RoleDescription
from mafia.roles.descriptions.texts import (
    DONT_PAY_FOR_VOTING,
    GUARANTEED_TO_KILL,
)
from states.game import UserFsm
from utils.roles import get_user_role_and_url


class Pirate(
    SpecialMoneyManagerMixin,
    SunsetKillerABC,
    ProcedureAfterVotingABC,
    ActiveRoleAtNightABC,
):
    role = "Пират"
    role_id: RolesLiteral = "pirate"
    photo = (
        "https://masterpiecer-images.s3.ya"
        "ndex.net/8e407a86a1a611ee8282f6f8c1ba65ae:upscaled"
    )
    grouping = Groupings.other
    purpose = (
        "Ты выбираешь меченого и смертника. Если после голосования смертника линчуют, "
        "а меченый голосовал за повешение, меченый погибнет"
    )
    message_to_group_after_action = "На ком-то поставили чёрную метку! Будьте предельно осторожны!"
    mail_message = "Кого пометишь и убьешь в случае ошибки?"
    notification_message = None
    need_to_monitor_interaction = False
    need_to_process = False
    payment_for_treatment = 4
    payment_for_murder = 12
    number_in_order_after_voting = 3
    extra_data = [ExtraCache(key="marked")]
    final_mission = "Убить {count} меченых"
    divider = 4
    payment_for_successful_operation = 17

    @property
    def role_description(self) -> RoleDescription:
        return RoleDescription(
            skill="Выбирает каждую ночь 2 игрока: сначала меченого, потом смертника. "
            "Если меченый на подтверждении линчевания проголосовал за, "
            "и смертник погиб по итогу, меченый умирает вместе с ним.",
            pay_for=["Убийство меченых"],
            features=[
                GUARANTEED_TO_KILL,
            ],
            limitations=[DONT_PAY_FOR_VOTING],
            wins_if="Убить столько меченых, сколько равняется количество игроков "
            "всего, деленное на 4. "
            f"Например, если играют 5 человек, нужно убить {5 // self.divider},"
            f" если 8, тогда {8 // self.divider} и т.д.",
        )

    def __init__(self):
        super().__init__()
        self.state_for_waiting_for_action = (
            UserFsm.PIRATE_CHOOSES_SUBJECT
        )
        self.aim_id: UserIdInt | None = None

    def kill_after_all_actions(
        self,
        game_data: GameCache,
        current_inactive_users: list[UserIdInt],
        cured_users: list[UserIdInt],
    ) -> tuple[UserIdInt, str] | None:
        if self.aim_id is None:
            return None
        self.successful_actions += 1
        role, url = get_user_role_and_url(
            game_data=game_data,
            processed_user_id=self.aim_id,
            all_roles=self.all_roles,
        )
        self.add_money_to_all_allies(
            game_data=game_data,
            money=17,
            beginning_message="Возмездное убийство",
            user_url=url,
            processed_role=role,
            at_night=False,
        )
        user_id = self.aim_id
        self.aim_id = None
        return (
            user_id,
            "😢Ты стал жертвой проклятья. Напиши же последние слова",
        )

    async def take_action_after_voting(
        self,
        game_data: GameCache,
        removed_user: list[UserIdInt],
        **kwargs,
    ):
        marked_users = game_data["marked"]
        if len(marked_users) != 2:
            return
        aim, bomber = marked_users
        if bomber != removed_user[0]:
            return
        if aim not in game_data["pros"]:
            return
        self.aim_id = aim

    def cancel_actions(
        self, game_data: GameCache, user_id: UserIdInt
    ):
        game_data["marked"].clear()
        return super().cancel_actions(
            game_data=game_data, user_id=user_id
        )
