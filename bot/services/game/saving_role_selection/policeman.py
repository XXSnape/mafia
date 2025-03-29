import asyncio

from constants.output import ROLE_IS_KNOWN, NUMBER_OF_NIGHT
from keyboards.inline.buttons.common import BACK_BTN
from keyboards.inline.callback_factory.recognize_user import (
    police_kill_cb_data,
    police_check_cb_data,
    PoliceActionIndexCbData,
)
from keyboards.inline.cb.cb_text import (
    POLICEMAN_KILLS_CB,
    POLICEMAN_CHECKS_CB,
)
from keyboards.inline.keypads.mailing import (
    send_selection_to_players_kb,
    kill_or_check_on_policeman,
)
from services.base import RouterHelper
from services.game.actions_at_night import (
    get_game_state_and_data,
    take_action_and_save_data,
    get_game_state_data_and_user_id,
    trace_all_actions,
    save_notification_message,
)
from services.game.roles import Policeman
from utils.tg import delete_message


class PolicemanSaver(RouterHelper):
    async def policeman_makes_choice(self):
        data = {
            POLICEMAN_KILLS_CB: [
                police_kill_cb_data,
                "Кого будешь убивать?",
            ],
            POLICEMAN_CHECKS_CB: [
                police_check_cb_data,
                "Кого будешь проверять?",
            ],
        }
        _, game_data = await get_game_state_and_data(
            tg_obj=self.callback,
            state=self.state,
            dispatcher=self.dispatcher,
        )
        police_action = data[self.callback.data]
        markup = send_selection_to_players_kb(
            players_ids=game_data["live_players_ids"],
            players=game_data["players"],
            extra_buttons=(BACK_BTN,),
            exclude=self.callback.from_user.id,
            user_index_cb=police_action[0],
        )
        await self.callback.message.edit_text(
            text=police_action[1], reply_markup=markup
        )

    async def policeman_cancels_selection(self):
        await self.callback.message.edit_text(
            text=Policeman.mail_message,
            reply_markup=kill_or_check_on_policeman(),
        )

    async def policeman_chose_to_kill(
        self, callback_data: PoliceActionIndexCbData
    ):
        await take_action_and_save_data(
            callback=self.callback,
            callback_data=callback_data,
            state=self.state,
            dispatcher=self.dispatcher,
        )

    async def policeman_chose_to_check(
        self, callback_data: PoliceActionIndexCbData
    ):
        game_state, game_data, checked_user_id = (
            await get_game_state_data_and_user_id(
                callback=self.callback,
                callback_data=callback_data,
                state=self.state,
                dispatcher=self.dispatcher,
            )
        )
        role_key = game_data["players"][str(checked_user_id)][
            "role_id"
        ]
        url = game_data["players"][str(checked_user_id)]["url"]
        game_data["disclosed_roles"].append(
            [checked_user_id, role_key]
        )
        await delete_message(self.callback.message)
        trace_all_actions(
            callback=self.callback,
            game_data=game_data,
            user_id=checked_user_id,
        )
        save_notification_message(
            game_data=game_data,
            processed_user_id=checked_user_id,
            message=ROLE_IS_KNOWN,
            current_user_id=self.callback.from_user.id,
        )
        await game_state.set_data(game_data)
        await self.callback.bot.send_message(
            chat_id=game_data["game_chat"],
            text="Армия насильно заставила кого-то показать документы",
        )
        await asyncio.gather(
            *(
                self.callback.bot.send_message(
                    chat_id=policeman_id,
                    text=NUMBER_OF_NIGHT.format(
                        game_data["number_of_night"]
                    )
                    + f"{game_data['players'][str(self.callback.from_user.id)]['pretty_role']} "
                    f"{game_data['players'][str(self.callback.from_user.id)]['url']} "
                    f"решил проверить {url}",
                )
                for policeman_id in game_data[Policeman.roles_key]
            )
        )
