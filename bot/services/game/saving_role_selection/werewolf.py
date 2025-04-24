from keyboards.inline.cb.cb_text import (
    WEREWOLF_TO_DOCTOR_CB,
    WEREWOLF_TO_MAFIA_CB,
    WEREWOLF_TO_POLICEMAN_CB,
)
from mafia.roles import (
    Doctor,
    Mafia,
    Policeman,
    Werewolf,
)
from services.base import RouterHelper
from services.game.game_assistants import  get_game_state_by_user_state
from utils.common import get_criminals_ids
from utils.informing import (
    get_profiles,
    notify_aliases_about_transformation,
    remind_commissioner_about_inspections,
    remind_criminals_about_inspections,
    send_a_lot_of_messages_safely,
)
from utils.pretty_text import make_pretty
from utils.roles import change_role
from utils.state import lock_state
from utils.tg import delete_message


class WerewolfSaver(RouterHelper):
    async def werewolf_turns_into(self):
        await delete_message(self.callback.message)
        data = {
            WEREWOLF_TO_MAFIA_CB: [Mafia(), Mafia.alias],
            WEREWOLF_TO_DOCTOR_CB: [Doctor(), Doctor.alias],
            WEREWOLF_TO_POLICEMAN_CB: [
                Policeman(),
                Policeman.alias,
            ],
        }
        user_id = self.callback.from_user.id
        current_roles = data[self.callback.data]
        roles_key = current_roles[0].roles_key
        are_there_many_senders = False
        game_state = await get_game_state_by_user_state(
            tg_obj=self.callback,
            user_state=self.state,
            dispatcher=self.dispatcher,
        )
        async with lock_state(game_state):
            game_data = await game_state.get_data()
            if len(game_data[roles_key]) == 0:
                new_role = current_roles[0]
            else:
                new_role = current_roles[1]
                are_there_many_senders = True
            change_role(
                game_data=game_data,
                previous_role=Werewolf(),
                new_role=new_role,
                user_id=user_id,
            )
            await self.state.set_state(
                new_role.state_for_waiting_for_action
            )
            await game_state.set_data(game_data)
        await self.callback.message.answer_photo(
            photo=new_role.photo,
            caption=f"Твоя новая роль - {make_pretty(new_role.role)}!",
        )
        await self.callback.bot.send_photo(
            chat_id=game_data["game_chat"],
            photo=new_role.photo,
            caption=f"{make_pretty(Werewolf.role)} принял "
            f"решение превратиться в {make_pretty(new_role.role)}. "
            f"Уже со следующего дня изменения в миропорядке вступят в силу.",
        )
        if are_there_many_senders:
            await notify_aliases_about_transformation(
                game_data=game_data,
                bot=self.callback.bot,
                new_role=new_role,
                user_id=user_id,
            )
        if self.callback.data == WEREWOLF_TO_POLICEMAN_CB:
            await self.callback.message.answer(
                text=remind_commissioner_about_inspections(game_data)
            )
        if self.callback.data == WEREWOLF_TO_MAFIA_CB:
            criminals = get_criminals_ids(game_data)
            text = (
                "В стане мафии пополнение! Вся команда:\n"
                + get_profiles(
                    players_ids=criminals,
                    players=game_data["players"],
                    role=True,
                )
            )
            await send_a_lot_of_messages_safely(
                bot=self.callback.bot, users=criminals, text=text
            )
            remind_text = remind_criminals_about_inspections(
                game_data
            )
            if remind_text:
                await self.callback.message.answer(text=remind_text)
