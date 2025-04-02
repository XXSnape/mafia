from cache.cache_types import GameCache, ExtraCache, UserIdInt
from keyboards.inline.keypads.mailing import kill_or_poison_kb
from mafia.roles.base import ActiveRoleAtNight
from mafia.roles.base.mixins import (
    ProcedureAfterNight,
    ProcedureAfterVoting,
)
from general.groupings import Groupings
from states.states import UserFsm
from utils.informing import get_profiles
from utils.roles import get_user_role_and_url


class Poisoner(
    ProcedureAfterVoting, ProcedureAfterNight, ActiveRoleAtNight
):
    role = "Отравитель"
    role_id = "poisoner"
    photo = "https://cdn.culture.ru/images/e949d2ef-65de-5336-aa98-50a16401045c"
    need_to_monitor_interaction = False
    purpose = (
        "Каждую ночь ты можешь либо отравить игрока, "
        "чтоб потом его убить, либо убить тех, кого отравил ранее."
    )
    message_to_group_after_action = None
    grouping = Groupings.other
    message_to_user_after_action = "Ты выбрал отравить {url}"
    mail_message = "Отравишь или убьешь?"
    notification_message = None
    payment_for_treatment = 0
    payment_for_murder = 15
    extra_data = [ExtraCache(key="poisoned", need_to_clear=False)]

    def __init__(self):
        self.state_for_waiting_for_action = (
            UserFsm.POISONER_CHOOSES_ACTION
        )
        self.victims = 0

    def get_money_for_victory_and_nights(
        self, game_data: GameCache, **kwargs
    ):
        if self.victims >= 3:
            return (
                self.victims * 20 * (len(game_data["players"]) // 4),
                0,
            )
        return 0, 0

    async def procedure_after_night(
        self,
        game_data: GameCache,
        murdered: list[int],
        killers_of: dict[UserIdInt, list[ActiveRoleAtNight]],
        **kwargs,
    ):
        poisoned = game_data["poisoned"]
        if poisoned and poisoned[1] == 1:
            murdered.extend(poisoned[0])
            for killed_id in poisoned[0]:
                killers_of[killed_id].append(self)

    async def accrual_of_overnight_rewards(
        self,
        game_data: GameCache,
        victims: set[int],
        killers_of: dict[UserIdInt, list[ActiveRoleAtNight]],
        **kwargs,
    ):
        poisoned = game_data["poisoned"]
        if not poisoned or poisoned[1] == 0:
            return
        for victim_id, roles in killers_of.items():
            if victim_id not in victims or self not in roles:
                continue
            self.victims += 1
            user_role, user_url = get_user_role_and_url(
                game_data=game_data,
                processed_user_id=victim_id,
                all_roles=self.all_roles,
            )
            money = user_role.payment_for_murder
            self.add_money_to_all_allies(
                game_data=game_data,
                money=money,
                user_url=user_url,
                processed_role=user_role,
                beginning_message="Убийство",
            )

    async def take_action_after_voting(
        self,
        game_data: GameCache,
        removed_user: list[UserIdInt | None],
        **kwargs,
    ):
        poisoned = game_data["poisoned"]
        if not poisoned:
            return
        if poisoned[1] == 0:
            murdered = [
                user_id
                for user_id in poisoned[0]
                if user_id not in game_data["live_players_ids"]
            ]
            removed_user_id = removed_user[0]
            if removed_user_id in poisoned[0]:
                murdered.append(removed_user_id)
            for murdered_id in murdered:
                poisoned[0].remove(murdered_id)
            return
        poisoned.clear()

    def cancel_actions(self, game_data: GameCache, user_id: int):
        if game_data["poisoned"]:
            if game_data["poisoned"][1] == 1:
                game_data["poisoned"][1] = 0
            else:
                if self.get_processed_user_id(game_data):
                    game_data["poisoned"][0].pop()
            return super().cancel_actions(
                game_data=game_data, user_id=user_id
            )

    def get_general_text_before_sending(
        self,
        game_data: GameCache,
    ) -> str | None:
        poisoned = game_data["poisoned"]
        if not poisoned:
            return "Нет отравленных людей"
        return "Ранее отравленные игроки\n" + get_profiles(
            players_ids=poisoned[0], players=game_data["players"]
        )

    def generate_markup(self, game_data: GameCache, **kwargs):
        poisoned = game_data["poisoned"]
        return kill_or_poison_kb(poisoned)
