from cache.cache_types import GameCache
from keyboards.inline.cb.cb_text import (
    WEREWOLF_TO_DOCTOR_CB,
    WEREWOLF_TO_MAFIA_CB,
    WEREWOLF_TO_POLICEMAN_CB,
)
from services.base import RouterHelper
from services.game.game_assistants import (
    get_game_state_by_user_state,
)
from utils.common import remove_from_expected_at_night
from utils.informing import (
    notify_aliases_about_transformation,
    remind_commissioner_about_inspections,
    remind_criminals_about_inspections,
)
from utils.roles import change_role
from utils.state import lock_state
from utils.tg import delete_message, resending_message

from mafia.roles import (
    Doctor,
    Mafia,
    Policeman,
    Werewolf,
)


class WerewolfSaver(RouterHelper):
    async def werewolf_turns_into(self):
        await delete_message(
            message=self.callback.message,
            raise_exception=True,
        )
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
            game_data: GameCache = await game_state.get_data()
            if (
                self.callback.from_user.id
                not in game_data["waiting_for_action_at_night"]
            ):
                return
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
            remove_from_expected_at_night(
                callback=self.callback,
                game_data=game_data,
            )
            await self.state.set_state(
                new_role.state_for_waiting_for_action
            )
            await game_state.set_data(game_data)
        await self.callback.message.answer_photo(
            photo=new_role.photo,
            caption=f"Твоя новая роль — {new_role.pretty_role}!",
            protect_content=game_data["settings"]["protect_content"],
        )
        if game_data["settings"]["show_roles_after_death"]:
            await resending_message(
                bot=self.callback.bot,
                chat_id=game_data["game_chat"],
                text=f"{Werewolf.pretty_role} принял "
                f"решение превратиться в {new_role.pretty_role}. "
                f"Уже со следующего дня изменения в миропорядке вступят в силу.",
                photo=new_role.photo,
            )
        if are_there_many_senders and (
            self.callback.data == WEREWOLF_TO_MAFIA_CB
            or game_data["settings"]["show_peaceful_allies"]
        ):
            await notify_aliases_about_transformation(
                game_data=game_data,
                bot=self.callback.bot,
                new_role=new_role,
                user_id=user_id,
            )
        if self.callback.data == WEREWOLF_TO_POLICEMAN_CB and (
            are_there_many_senders is False
            or game_data["settings"]["show_peaceful_allies"]
        ):
            await self.callback.message.answer(
                text=remind_commissioner_about_inspections(game_data)
            )
        if self.callback.data == WEREWOLF_TO_MAFIA_CB:
            remind_text = remind_criminals_about_inspections(
                game_data
            )
            if remind_text:
                await self.callback.message.answer(
                    text=remind_text,
                    protect_content=game_data["settings"][
                        "protect_content"
                    ],
                )
