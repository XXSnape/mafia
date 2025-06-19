from cache.cache_types import GameCache, RolesLiteral, UserIdInt
from cache.extra import ExtraCache
from general.groupings import Groupings
from mafia.roles.base import ActiveRoleAtNightABC
from mafia.roles.base.mixins import (
    ObligatoryKillerABC,
    ProcedureAfterVotingABC,
)
from mafia.roles.descriptions.description import RoleDescription
from states.game import UserFsm
from utils.roles import get_user_role_and_url


class Pirate(
    ObligatoryKillerABC,
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
    mail_message = "Кого пометишь и убьешь в случае ошибки жертвы?"
    notification_message = None
    payment_for_treatment = 4
    payment_for_murder = 12
    extra_data = [ExtraCache(key="marked")]

    @property
    def role_description(self) -> RoleDescription:
        pass

    def __init__(self):
        self.state_for_waiting_for_action = (
            UserFsm.PIRATE_CHOOSES_SUBJECT
        )

    def kill_after_all_actions(
        self,
        game_data: GameCache,
        current_inactive_users: list[UserIdInt],
    ) -> tuple[UserIdInt, str] | None: ...

    async def take_action_after_voting(
        self,
        game_data: GameCache,
        **kwargs,
    ):
        pass

    def cancel_actions(
        self, game_data: GameCache, user_id: UserIdInt
    ):
        game_data["marked"].clear()
        return super().cancel_actions(
            game_data=game_data, user_id=user_id
        )
