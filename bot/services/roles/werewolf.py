from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from cache.cache_types import GameCache
from cache.roleses import Groupings
from keyboards.inline.keypads.mailing import send_transformation_kb
from services.roles.base import ActiveRoleAtNight
from states.states import UserFsm


class Werewolf(ActiveRoleAtNight):
    role = "Оборотень"
    need_to_monitor_interaction = False
    photo = (
        "https://sun9-42.userapi.com/impf/c303604/v303604068/170c/FXQRtSk8e28.jpg?size=484x604&quality="
        "96&sign=bf5555ef2b801954b0b92848975525fd&type=album"
        "?imw=512&imh=512&ima=fit&impolicy=Letterbox&imcolor=%23000000&letterbox=true"
    )
    grouping = Groupings.civilians
    purpose = "На 4 ночь ты сможешь превратиться в мафию, маршала или доктора."
    mail_message = "Реши, в кого сегодня превратишься!"

    def __init__(self):
        self.state_for_waiting_for_action = (
            UserFsm.WEREWOLF_TURNS_INTO
        )

    def generate_markup(
        self,
        player_id: int,
        game_data: GameCache,
        extra_buttons: tuple[InlineKeyboardButton, ...] = (),
    ):
        return send_transformation_kb(game_data)

    async def mailing(
        self,
        game_data: GameCache,
        own_markup: InlineKeyboardMarkup | None = None,
    ):
        if game_data["number_of_night"] == 2:  # TODO 4
            await super().mailing(
                game_data=game_data,
            )
