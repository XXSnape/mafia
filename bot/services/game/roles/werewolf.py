from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from cache.cache_types import GameCache
from keyboards.inline.keypads.mailing import send_transformation_kb
from services.game.roles.base import ActiveRoleAtNight
from services.game.roles.base.mixins import ProcedureAfterNight
from states.states import UserFsm


class Werewolf(ProcedureAfterNight, ActiveRoleAtNight):
    role = "Оборотень"
    need_to_monitor_interaction = False
    photo = (
        "https://sun9-42.userapi.com/impf/c303604/v303604068/170c/FXQRtSk8e28.jpg?size=484x604&quality="
        "96&sign=bf5555ef2b801954b0b92848975525fd&type=album"
        "?imw=512&imh=512&ima=fit&impolicy=Letterbox&imcolor=%23000000&letterbox=true"
    )
    purpose = "На 4ую ночь ты сможешь превратиться в мафию, маршала или доктора."
    mail_message = "Реши, в кого сегодня превратишься!"
    payment_for_treatment = 11
    payment_for_murder = 12
    number_of_night_for_transformation = 2

    async def procedure_after_night(
        self,
        game_data: GameCache,
        **kwargs,
    ):
        from general.collection_of_roles import get_data_with_roles

        if (
            game_data["number_of_night"]
            == self.number_of_night_for_transformation
        ):
            for player_data in game_data["players"].values():
                if player_data["role_id"] not in self.all_roles:
                    new_role = get_data_with_roles(
                        player_data["role_id"]
                    )
                    new_role(
                        dispatcher=self.dispatcher,
                        bot=self.bot,
                        state=self.state,
                        all_roles=self.all_roles,
                    )
                    self.all_roles[player_data["role_id"]] = new_role

    def __init__(self):
        self.state_for_waiting_for_action = (
            UserFsm.WEREWOLF_TURNS_INTO
        )

    async def accrual_of_overnight_rewards(
        self,
        **kwargs,
    ):
        pass

    def generate_markup(self, game_data: GameCache, **kwargs):
        return send_transformation_kb(game_data)

    def allow_sending_mailing(self, game_data: GameCache):
        if (
            game_data["number_of_night"]
            == self.number_of_night_for_transformation
        ):  # TODO 4
            return True
