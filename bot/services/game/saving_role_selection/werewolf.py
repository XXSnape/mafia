from keyboards.inline.cb.cb_text import WEREWOLF_TO_MAFIA_CB, WEREWOLF_TO_DOCTOR_CB, WEREWOLF_TO_POLICEMAN_CB
from services.base import RouterHelper
from services.game.actions_at_night import get_game_state_and_data
from services.game.roles import Mafia, MafiaAlias, Doctor, DoctorAlias, Policeman, PolicemanAlias, Werewolf
from utils.tg import delete_message
from utils.pretty_text import make_pretty
from utils.informing import notify_aliases_about_transformation, remind_commissioner_about_inspections
from utils.roles import change_role


class WerewolfSaver(RouterHelper):
    async def werewolf_turns_into(self):
        data = {
            WEREWOLF_TO_MAFIA_CB: [
                [Mafia(), "don"],
                [MafiaAlias(), "mafia"],
            ],
            WEREWOLF_TO_DOCTOR_CB: [
                [Doctor(), "doctor"],
                [DoctorAlias(), "nurse"],
            ],
            WEREWOLF_TO_POLICEMAN_CB: [
                [Policeman(), "policeman"],
                [PolicemanAlias(), "general"],
            ],
        }
        game_state, game_data = await get_game_state_and_data(
            tg_obj=self.callback, state=self.state, dispatcher=self.dispatcher
        )

        user_id = self.callback.from_user.id
        current_roles = data[self.callback.data]
        roles_key = current_roles[0][0].roles_key
        await delete_message(self.callback.message)
        are_there_many_senders = False
        if len(game_data[roles_key]) == 0:
            role_id = current_roles[0][1]
            new_role = current_roles[0][0]
        else:
            role_id = current_roles[1][1]
            new_role = current_roles[1][0]
            are_there_many_senders = True
        change_role(
            game_data=game_data,
            previous_role=Werewolf(),
            new_role=new_role,
            role_id=role_id,
            user_id=user_id,
        )
        await game_state.set_data(game_data)
        await self.state.set_state(new_role.state_for_waiting_for_action)
        await self.callback.message.answer_photo(
            photo=new_role.photo,
            caption=f"Твоя новая роль - {make_pretty(new_role.role)}!",
        )
        await self.callback.bot.send_photo(
            chat_id=game_data["game_chat"],
            photo=new_role.photo,
            caption=f"{make_pretty(Werewolf.role)} принял решение превратиться в {make_pretty(new_role.role)}. "
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
