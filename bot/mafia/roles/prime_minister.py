from cache.cache_types import GameCache, RolesLiteral, UserIdInt
from mafia.roles.base import RoleABC
from mafia.roles.base.mixins import ProcedureAfterVotingABC
from mafia.roles.descriptions.description import RoleDescription
from mafia.roles.descriptions.texts import (
    KILLING_PLAYER,
    SAVING_PLAYER,
)
from utils.pretty_text import make_build
from utils.roles import get_user_role_and_url


class PrimeMinister(ProcedureAfterVotingABC, RoleABC):
    role = "Премьер-министр"
    role_id: RolesLiteral = "prime_minister"
    photo = (
        "https://avatars.mds.yandex.net/i?id=fb2e5e825d183d5344d93bc563"
        "6bc4c4_l-5084109-images-thumbs&n=13"
    )
    purpose = "Твой голос стоит как 2!"
    payment_for_treatment = 12
    payment_for_murder = 12

    @property
    def role_description(self) -> RoleDescription:
        return RoleDescription(
            skill="Днём имеет 2 голоса при подтверждении повешения",
            pay_for=[KILLING_PLAYER, SAVING_PLAYER],
            features=[
                "Не может быть повешен на дневном голосовании"
            ],
        )

    def get_money_for_voting(self, voted_role: RoleABC):
        return super().get_money_for_voting(voted_role) * 2

    async def take_action_after_voting(
        self,
        game_data: GameCache,
        is_not_there_removed: bool,
        initial_removed_user_id: UserIdInt | None,
        removed_user: list[int],
        **kwargs,
    ):
        if removed_user[0] in game_data[self.roles_key]:
            await self.bot.send_message(
                chat_id=game_data["game_chat"],
                text=make_build(
                    "🤨Крайне странно вешать лидеров мнений.\n"
                    "Жители это осознали и разошлись..."
                ),
            )
            removed_user[:] = [0]
            return
        if (
            is_not_there_removed is False
            or not game_data[self.roles_key]
        ):
            return
        if game_data[self.roles_key][0] in game_data["cons"]:
            role, url = get_user_role_and_url(
                game_data=game_data,
                processed_user_id=initial_removed_user_id,
                all_roles=self.all_roles,
            )
            self.add_money_to_all_allies(
                game_data=game_data,
                money=int(role.payment_for_treatment * 1.5),
                beginning_message="Спасение от повешения",
                user_url=url,
                processed_role=role,
                at_night=False,
            )
