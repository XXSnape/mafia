import asyncio

from aiogram import Dispatcher, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from constants.output import NUMBER_OF_NIGHT
from keyboards.inline.callback_factory.recognize_user import (
    UserActionIndexCbData,
)
from services.game.actions_at_night import (
    take_action_and_register_user,
)
from services.game.roles import Mafia, Traitor
from services.game.saving_role_selection import TraitorSaver
from states.states import UserFsm
from utils.utils import make_pretty

router = Router(name=__name__)


@router.callback_query(
    UserFsm.TRAITOR_FINDS_OUT,
    UserActionIndexCbData.filter(),
)
async def traitor_finds_out(
    callback: CallbackQuery,
    callback_data: UserActionIndexCbData,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    saver = TraitorSaver(
        callback=callback,
        state=state,
        dispatcher=dispatcher
    )
    await saver.traitor_finds_out(callback_data=callback_data)
    # game_state, game_data, user_id = (
    #     await take_action_and_register_user(
    #         callback=callback,
    #         callback_data=callback_data,
    #         state=state,
    #         dispatcher=dispatcher,
    #     )
    # )
    # url = game_data["players"][str(user_id)]["url"]
    # role = game_data["players"][str(user_id)]["pretty_role"]
    # await asyncio.gather(
    #     *(
    #         callback.bot.send_message(
    #             chat_id=player_id,
    #             text=NUMBER_OF_NIGHT.format(
    #                 game_data["number_of_night"]
    #             )
    #             + f"{make_pretty(Traitor.role)} проверил и узнал, что {url} - {role}",
    #         )
    #         for player_id in game_data[Mafia.roles_key]
    #         + game_data[Traitor.roles_key]
    #     )
    # )
