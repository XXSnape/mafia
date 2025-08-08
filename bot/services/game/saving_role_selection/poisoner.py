from cache.cache_types import GameCache
from keyboards.inline.buttons.common import BACK_BTN
from keyboards.inline.callback_factory.recognize_user import (
    UserActionIndexCbData,
)
from keyboards.inline.keypads.mailing import (
    kill_or_poison_kb,
    send_selection_to_players_kb,
)
from services.base import RouterHelper
from services.game.game_assistants import (
    get_game_state_by_user_state,
    send_messages_to_user_and_group,
    take_action_and_save_data,
)
from states.game import UserFsm
from utils.common import remove_from_expected_at_night
from utils.state import lock_state
from utils.tg import delete_message

from mafia.roles import Poisoner


class PoisonerSaver(RouterHelper):
    async def poisoner_chose_to_kill(self):
        await delete_message(self.callback.message)
        game_state = await get_game_state_by_user_state(
            tg_obj=self.callback,
            user_state=self.state,
            dispatcher=self.dispatcher,
        )
        async with lock_state(game_state):
            game_data = await game_state.get_data()
            poisoned = game_data["poisoned"]
            poisoned[1] = True
            remove_from_expected_at_night(
                callback=self.callback, game_data=game_data
            )
            await game_state.set_data(game_data)

        await send_messages_to_user_and_group(
            callback=self.callback,
            game_data=game_data,
            message_to_user="Ты решил всех убить!",
            message_to_group=False,
        )

    async def poisoner_poisons(self):
        game_state = await get_game_state_by_user_state(
            tg_obj=self.callback,
            user_state=self.state,
            dispatcher=self.dispatcher,
        )
        game_data: GameCache = await game_state.get_data()
        poisoned = game_data["poisoned"]
        exclude = (poisoned[0] if poisoned else []) + [
            self.callback.from_user.id
        ]
        await self.state.set_state(UserFsm.POISONER_CHOSE_TO_KILL)
        await self.callback.message.edit_text(
            "Кого собираешься отравить?",
            reply_markup=send_selection_to_players_kb(
                players_ids=game_data["live_players_ids"],
                players=game_data["players"],
                extra_buttons=(BACK_BTN,),
                exclude=exclude,
            ),
        )

    async def poisoner_cancels_selection(self):
        game_state = await get_game_state_by_user_state(
            tg_obj=self.callback,
            user_state=self.state,
            dispatcher=self.dispatcher,
        )
        game_data: GameCache = await game_state.get_data()
        await self.state.set_state(UserFsm.POISONER_CHOOSES_ACTION)
        await self.callback.message.edit_text(
            text=Poisoner.mail_message,
            reply_markup=kill_or_poison_kb(game_data=game_data),
        )

    async def poisoner_chose_victim(
        self, callback_data: UserActionIndexCbData
    ):
        game_state, user_id = await take_action_and_save_data(
            callback=self.callback,
            callback_data=callback_data,
            state=self.state,
            dispatcher=self.dispatcher,
        )
        if game_state is None:
            return
        async with lock_state(game_state):
            game_data = await game_state.get_data()
            poisoned = game_data["poisoned"]
            if poisoned:
                poisoned[0].append(user_id)
            else:
                poisoned[:] = [[user_id], False]
            await game_state.set_data(game_data)
