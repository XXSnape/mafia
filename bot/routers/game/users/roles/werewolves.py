from aiogram import Dispatcher, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from keyboards.inline.cb.cb_text import (
    WEREWOLF_TO_DOCTOR_CB,
    WEREWOLF_TO_MAFIA_CB,
    WEREWOLF_TO_POLICEMAN_CB,
)
from services.game.actions_at_night import get_game_state_and_data
from services.game.roles import (
    Werewolf,
    Mafia,
    MafiaAlias,
    Doctor,
    DoctorAlias,
    Policeman,
    PolicemanAlias,
)
from services.game.saving_role_selection import WerewolfSaver
from states.states import UserFsm
from utils.tg import delete_message
from utils.utils import (
    make_pretty,
)
from utils.validators import (
    remind_commissioner_about_inspections,
    change_role,
    notify_aliases_about_transformation,
)

router = Router(name=__name__)


@router.callback_query(
    UserFsm.WEREWOLF_TURNS_INTO,
    F.data.in_(
        [
            WEREWOLF_TO_MAFIA_CB,
            WEREWOLF_TO_DOCTOR_CB,
            WEREWOLF_TO_POLICEMAN_CB,
        ]
    ),
)
async def werewolf_turns_into(
    callback: CallbackQuery,
    state: FSMContext,
    dispatcher: Dispatcher,
):
    saver = WerewolfSaver(
        callback=callback,
        state=state,
        dispatcher=dispatcher
    )
    await saver.werewolf_turns_into()
    # data = {
    #     WEREWOLF_TO_MAFIA_CB: [
    #         [Mafia(), "don"],
    #         [MafiaAlias(), "mafia"],
    #     ],
    #     WEREWOLF_TO_DOCTOR_CB: [
    #         [Doctor(), "doctor"],
    #         [DoctorAlias(), "nurse"],
    #     ],
    #     WEREWOLF_TO_POLICEMAN_CB: [
    #         [Policeman(), "policeman"],
    #         [PolicemanAlias(), "general"],
    #     ],
    # }
    # game_state, game_data = await get_game_state_and_data(
    #     tg_obj=callback, state=state, dispatcher=dispatcher
    # )
    #
    # user_id = callback.from_user.id
    # current_roles = data[callback.data]
    # roles_key = current_roles[0][0].roles_key
    # await delete_message(callback.message)
    # are_there_many_senders = False
    # if len(game_data[roles_key]) == 0:
    #     enum_name = current_roles[0][1]
    #     new_role = current_roles[0][0]
    # else:
    #     enum_name = current_roles[1][1]
    #     new_role = current_roles[1][0]
    #     are_there_many_senders = True
    # change_role(
    #     game_data=game_data,
    #     previous_role=Werewolf(),
    #     new_role=new_role,
    #     role_key=enum_name,
    #     user_id=user_id,
    # )
    # await game_state.set_data(game_data)
    # await state.set_state(new_role.state_for_waiting_for_action)
    # await callback.message.answer_photo(
    #     photo=new_role.photo,
    #     caption=f"Твоя новая роль - {make_pretty(new_role.role)}!",
    # )
    # await callback.bot.send_photo(
    #     chat_id=game_data["game_chat"],
    #     photo=new_role.photo,
    #     caption=f"{make_pretty(Werewolf.role)} принял решение превратиться в {make_pretty(new_role.role)}. "
    #     f"Уже со следующего дня изменения в миропорядке вступят в силу.",
    # )
    # if are_there_many_senders:
    #     await notify_aliases_about_transformation(
    #         game_data=game_data,
    #         bot=callback.bot,
    #         new_role=new_role,
    #         user_id=user_id,
    #     )
    # if callback.data == WEREWOLF_TO_POLICEMAN_CB:
    #     await callback.message.answer(
    #         text=remind_commissioner_about_inspections(game_data)
    #     )
