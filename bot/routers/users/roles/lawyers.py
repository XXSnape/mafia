from aiogram import Dispatcher, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from general.collection_of_roles import Roles
from keyboards.inline.callback_factory.recognize_user import UserActionIndexCbData
from services.actions_at_night import take_action_and_register_user
from states.states import UserFsm

router = Router(name=__name__)


@router.callback_query(
    UserFsm.LAWYER_PROTECTS, UserActionIndexCbData.filter()
)
async def lawyer_protects(
    callback: CallbackQuery,
    callback_data: UserActionIndexCbData,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    await take_action_and_register_user(
        callback=callback,
        callback_data=callback_data,
        state=state,
        dispatcher=dispatcher,
        # message_to_group="Кому-то обеспечена защита лучшими адвокатами города!",
        # message_to_user="Ты выбрал защитить {url}",
        role=Roles.lawyer,
        # last_processed_user_key="last_forgiven",
        # list_to_process_key="have_alibi",
    )
    # game_state, game_data, protected_user_id = (
    #     await get_user_id_and_inform_players(
    #         callback=callback,
    #         callback_data=callback_data,
    #         state=state,
    #         dispatcher=dispatcher,
    #         message_to_group="Кому-то обеспечена защита лучшими адвокатами города!",
    #         message_to_user="Ты выбрал защитить {url}",
    #     )
    # )
    # game_data["have_alibi"].append(protected_user_id)
    # game_data["last_forgiven"] = protected_user_id
    # await game_state.set_data(game_data)
    # user_data: UserCache = await state.get_data()
    # game_state = await get_state_and_assign(
    #     dispatcher=dispatcher,
    #     chat_id=user_data["game_chat"],
    #     bot_id=callback.bot.id,
    # )
    # game_data: GameCache = await game_state.get_data()
    # await callback.bot.send_message(
    #     chat_id=user_data["game_chat"],
    #     text="Доктор спешит кому-то на помощь!",
    # )
    #
    # recovered_user_id = game_data["players_ids"][
    #     callback_data.user_index
    # ]
    # # await callback.bot.send_message(
    # #     chat_id=recovered_user_id,
    # #     text="Врачи не забыли клятву Гиппократа и делают все возможное для твоего спасения!",
    # # )
    # game_data["recovered"].append(recovered_user_id)
    # url = game_data["players"][str(recovered_user_id)]["url"]
    # game_data["last_treated"] = recovered_user_id
    # await callback.message.delete()
    # await callback.message.answer(f"Ты выбрал вылечить {url}")
    # await game_state.set_data(game_data)
