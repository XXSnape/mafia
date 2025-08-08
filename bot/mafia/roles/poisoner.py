from cache.cache_types import (
    GameCache,
    PlayersIds,
    RolesLiteral,
    UserIdInt,
)
from cache.extra import ExtraCache
from general.groupings import Groupings
from general.text import (
    ATTEMPT_TO_KILL,
)
from keyboards.inline.keypads.mailing import kill_or_poison_kb
from states.game import UserFsm
from utils.informing import get_profiles
from utils.roles import get_user_role_and_url

from mafia.roles.base import ActiveRoleAtNightABC
from mafia.roles.base.mixins import (
    FinisherOfNight,
    KillersOf,
    ProcedureAfterNightABC,
    SpecialMoneyManagerMixin,
)
from mafia.roles.descriptions.description import RoleDescription
from mafia.roles.descriptions.texts import (
    DONT_PAY_FOR_VOTING,
)


class Poisoner(
    SpecialMoneyManagerMixin,
    FinisherOfNight,
    ProcedureAfterNightABC,
    ActiveRoleAtNightABC,
):
    role = "Отравитель"
    role_id: RolesLiteral = "poisoner"
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
    notification_message = ATTEMPT_TO_KILL
    payment_for_treatment = 0
    payment_for_murder = 15
    extra_data = [ExtraCache(key="poisoned", need_to_clear=False)]
    final_mission = "Убить {count} человек"
    divider = 4
    payment_for_successful_operation = 16

    @property
    def role_description(self) -> RoleDescription:
        return RoleDescription(
            skill="За 1 ночь может либо отравить игрока, либо убить всех отравленных ранее",
            pay_for=["Убийство любого игрока"],
            limitations=[DONT_PAY_FOR_VOTING],
            wins_if="Побеждает, если убьет столько игроков, "
            "сколько равняется количество игроков всего, "
            "делённое нацело на 4 и еще одного. "
            f"Например, если в игре 5 человек, то нужно убить {5 // self.divider}, "
            f"если 8, то {8 // self.divider} и т.д.",
        )

    def __init__(self):
        super().__init__()
        self.state_for_waiting_for_action = (
            UserFsm.POISONER_CHOOSES_ACTION
        )

    async def procedure_after_night(
        self,
        game_data: GameCache,
        murdered: PlayersIds,
        killers_of: KillersOf,
        **kwargs,
    ):
        poisoned = game_data["poisoned"]
        if poisoned and poisoned[1] is True:
            murdered.extend(poisoned[0])
            for killed_id in poisoned[0]:
                killers_of[killed_id].append(self)

    async def accrual_of_overnight_rewards(
        self,
        game_data: GameCache,
        victims: set[UserIdInt],
        killers_of: KillersOf,
        **kwargs,
    ):
        poisoned = game_data["poisoned"]
        if not poisoned or poisoned[1] is False:
            return
        for victim_id, roles in killers_of.items():
            if self not in roles:
                continue
            game_data["messages_after_night"].append(
                [victim_id, self.notification_message]
            )
            if victim_id not in victims:
                continue
            self.successful_actions += 1
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

    def leave_notification_message(
        self,
        game_data: GameCache,
        context_message: str | None = None,
    ):
        return

    async def end_night(self, game_data: GameCache):
        poisoned = game_data["poisoned"]
        if not poisoned:
            return
        if poisoned[1] is False:
            murdered = [
                user_id
                for user_id in poisoned[0]
                if user_id not in game_data["live_players_ids"]
            ]
            for murdered_id in murdered:
                poisoned[0].remove(murdered_id)
            # После превращания новый отравитель может оказаться в списке потенциально убитых
            for user_id in game_data[self.roles_key]:
                if user_id in poisoned[0]:
                    poisoned[0].remove(user_id)
            return
        poisoned.clear()

    def cancel_actions(self, game_data: GameCache, user_id: int):
        if game_data["poisoned"]:
            if game_data["poisoned"][1] is True:
                game_data["poisoned"][1] = False
                return True
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
        if not poisoned or not poisoned[0]:
            return "Нет отравленных людей"
        return "Ранее отравленные игроки\n" + get_profiles(
            players_ids=poisoned[0], players=game_data["players"]
        )

    def generate_markup(self, game_data: GameCache, **kwargs):
        return kill_or_poison_kb(game_data=game_data)
