from keyboards.inline.buttons.common import BACK_BTN
from keyboards.inline.callback_factory.recognize_user import (
    UserActionIndexCbData,
)
from keyboards.inline.keypads.mailing import (
    send_selection_to_players_kb,
)
from services.base import RouterHelper
from services.game.game_assistants import (
    get_game_data_and_user_id,
    get_game_state_by_user_state,
    send_messages_to_user_and_group,
    trace_all_actions,
)
from utils.state import lock_state
from utils.tg import delete_message

from mafia.roles import ActiveRoleAtNightABC


class ChoosingSubjectAndObject(RouterHelper):
    role: type[ActiveRoleAtNightABC] = None
    key_for_saving_data = None
    message_when_selecting_subject: str | None = None
    message_after_selecting_object: str | None = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state_when_selecting_object = None

    async def chooses_subject(
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
            game_data[self.key_for_saving_data] = [user_id]
            await self.state.set_state(
                self.state_when_selecting_object
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
            text=self.message_when_selecting_subject.format(url=url),
            reply_markup=markup,
        )

    async def cancels_selection(self):
        game_state = await get_game_state_by_user_state(
            tg_obj=self.callback,
            user_state=self.state,
            dispatcher=self.dispatcher,
        )
        role = self.role()
        async with lock_state(game_state):
            game_data = await game_state.get_data()
            game_data[self.key_for_saving_data].clear()
            await self.state.set_state(
                role.state_for_waiting_for_action
            )
            await game_state.set_data(game_data)

        await self.callback.message.edit_text(
            text=role.mail_message,
            reply_markup=role.generate_markup(
                player_id=self.callback.from_user.id,
                game_data=game_data,
            ),
        )

    async def chooses_object(
        self, callback_data: UserActionIndexCbData
    ):
        await delete_message(
            message=self.callback.message,
            raise_exception=True,
        )
        game_state = await get_game_state_by_user_state(
            tg_obj=self.callback,
            user_state=self.state,
            dispatcher=self.dispatcher,
        )
        async with lock_state(game_state):
            game_data, user_id = await get_game_data_and_user_id(
                game_state=game_state, callback_data=callback_data
            )
            if (
                self.callback.from_user.id
                not in game_data["waiting_for_action_at_night"]
            ):
                return
            users = game_data[self.key_for_saving_data]
            users.append(user_id)
            trace_all_actions(
                callback=self.callback,
                game_data=game_data,
                user_id=users[0],
            )
            await game_state.set_data(game_data)
        subject_url = game_data["players"][str(users[0])]["url"]
        object_url = game_data["players"][str(users[1])]["url"]
        await send_messages_to_user_and_group(
            callback=self.callback,
            game_data=game_data,
            message_to_user=self.message_after_selecting_object.format(
                subject_url=subject_url,
                object_url=object_url,
            ),
            current_role=self.role(),
            message_to_group=game_data["settings"][
                "show_roles_after_death"
            ],
        )
