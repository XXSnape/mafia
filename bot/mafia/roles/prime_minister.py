from cache.cache_types import GameCache
from mafia.roles.base import Role
from mafia.roles.base.mixins import ProcedureAfterVoting
from utils.roles import get_user_role_and_url


class PrimeMinister(ProcedureAfterVoting, Role):
    role = "Премьер-министр"
    photo = (
        "https://avatars.mds.yandex.net/i?id=fb2e5e825d183d5344d93bc563"
        "6bc4c4_l-5084109-images-thumbs&n=13"
    )
    purpose = "Твой голос стоит как 2!"
    payment_for_treatment = 12
    payment_for_murder = 12

    def get_money_for_voting(self, voted_role: Role):
        return super().get_money_for_voting(voted_role) * 2

    async def take_action_after_voting(
        self,
        game_data: GameCache,
        is_not_there_removed: bool,
        initial_removed_user_id: int,
        **kwargs,
    ):
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
