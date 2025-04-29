from keyboards.inline.buttons.common import BACK_BTN
from keyboards.inline.callback_factory.recognize_user import (
    UserActionIndexCbData,
)
from keyboards.inline.keypads.mailing import (
    send_selection_to_players_kb,
)
from mafia.roles import Instigator
from services.base import RouterHelper
from services.game.game_assistants import (
    get_game_data_and_user_id,
    get_game_state_by_user_state,
    send_messages_to_user_and_group,
    trace_all_actions,
)
from states.game import UserFsm
from utils.state import lock_state
from utils.tg import delete_message


class InstigatorSaver(RouterHelper):
    async def instigator_chooses_subject(
        self, callback_data: UserActionIndexCbData
    ):
        game_state = await get_game_state_by_user_state(
            tg_obj=self.callback,
            user_state=self.state,
            dispatcher=self.dispatcher,
        )
        async with lock_state(game_state):
            game_data, user_id = await get_game_data_and_user_id(
                game_state=game_state, callback_data=callback_data
            )
            game_data["deceived"] = [user_id]
            await self.state.set_state(
                UserFsm.INSTIGATOR_CHOOSES_OBJECT
            )
            await game_state.set_data(game_data)
        url = game_data["players"][str(user_id)]["url"]
        markup = send_selection_to_players_kb(
            players_ids=game_data["live_players_ids"],
            players=game_data["players"],
            extra_buttons=(BACK_BTN,),
            exclude=user_id,
        )
        await self.callback.message.edit_text(
            text=f"За кого должен проголосовать {url}?",
            reply_markup=markup,
        )

    async def instigator_cancels_selection(self):
        game_state = await get_game_state_by_user_state(
            tg_obj=self.callback,
            user_state=self.state,
            dispatcher=self.dispatcher,
        )
        async with lock_state(game_state):
            game_data = await game_state.get_data()
            game_data["deceived"].clear()
            await self.state.set_state(
                UserFsm.INSTIGATOR_CHOOSES_SUBJECT
            )
            await game_state.set_data(game_data)
        instigator = Instigator()
        await self.callback.message.edit_text(
            text=instigator.mail_message,
            reply_markup=instigator.generate_markup(
                player_id=self.callback.from_user.id,
                game_data=game_data,
            ),
        )

    async def instigator_chooses_object(
        self, callback_data: UserActionIndexCbData
    ):
        await delete_message(self.callback.message)
        game_state = await get_game_state_by_user_state(
            tg_obj=self.callback,
            user_state=self.state,
            dispatcher=self.dispatcher,
        )
        async with lock_state(game_state):
            game_data, user_id = await get_game_data_and_user_id(
                game_state=game_state, callback_data=callback_data
            )
            deceived_user = game_data["deceived"]
            deceived_user.append(user_id)
            trace_all_actions(
                callback=self.callback,
                game_data=game_data,
                user_id=user_id,
            )
            await game_state.set_data(game_data)
        subject_url = game_data["players"][str(deceived_user[0])][
            "url"
        ]
        object_url = game_data["players"][str(deceived_user[1])][
            "url"
        ]
        await send_messages_to_user_and_group(
            callback=self.callback,
            game_data=game_data,
            message_to_user=f"Днём {subject_url} проголосует за "
            f"{object_url}, если попытается голосовать",
            current_role=Instigator(),
            message_to_group=game_data["settings"][
                "show_roles_after_death"
            ],
        )
