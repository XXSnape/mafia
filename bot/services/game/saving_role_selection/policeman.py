from general.text import NUMBER_OF_NIGHT
from keyboards.inline.buttons.common import BACK_BTN
from keyboards.inline.callback_factory.recognize_user import (
    PoliceActionIndexCbData,
    police_check_cb_data,
    police_kill_cb_data,
)
from keyboards.inline.cb.cb_text import (
    POLICEMAN_CHECKS_CB,
    POLICEMAN_KILLS_CB,
)
from keyboards.inline.keypads.mailing import (
    kill_or_check_on_policeman,
    send_selection_to_players_kb,
)
from mafia.roles import Policeman
from services.base import RouterHelper
from services.game.game_assistants import (
    get_game_state_and_data,
    get_game_state_data_and_user_id,
    take_action_and_save_data,
    trace_all_actions,
)
from utils.informing import send_a_lot_of_messages_safely
from utils.tg import delete_message


class PolicemanSaver(RouterHelper):
    async def policeman_makes_choice(self):
        _, game_data = await get_game_state_and_data(
            tg_obj=self.callback,
            state=self.state,
            dispatcher=self.dispatcher,
        )
        data = {
            POLICEMAN_KILLS_CB: [
                police_kill_cb_data,
                "Кого будешь убивать?",
                [self.callback.from_user.id],
            ],
            POLICEMAN_CHECKS_CB: [
                police_check_cb_data,
                "Кого будешь проверять?",
                game_data[Policeman.roles_key],
            ],
        }
        police_action = data[self.callback.data]
        markup = send_selection_to_players_kb(
            players_ids=game_data["live_players_ids"],
            players=game_data["players"],
            extra_buttons=(BACK_BTN,),
            exclude=police_action[2],
            user_index_cb=police_action[0],
        )

        await self.callback.message.edit_text(
            text=police_action[1], reply_markup=markup
        )

    async def policeman_cancels_selection(self):
        _, game_data = await get_game_state_and_data(
            tg_obj=self.callback,
            state=self.state,
            dispatcher=self.dispatcher,
        )
        await self.callback.message.edit_text(
            text=Policeman.mail_message,
            reply_markup=kill_or_check_on_policeman(
                number_of_night=game_data["number_of_night"]
            ),
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
        await delete_message(self.callback.message)
        game_state, game_data, checked_user_id = (
            await get_game_state_data_and_user_id(
                callback=self.callback,
                callback_data=callback_data,
                state=self.state,
                dispatcher=self.dispatcher,
            )
        )
        url = game_data["players"][str(checked_user_id)]["url"]
        game_data["disclosed_roles"].append(checked_user_id)
        await trace_all_actions(
            callback=self.callback,
            game_data=game_data,
            user_id=checked_user_id,
            current_role=Policeman(),
            message_to_user=False,
            message_to_group="Армия насильно заставила кого-то показать документы!",
        )
        await game_state.set_data(game_data)
        text = NUMBER_OF_NIGHT.format(
            game_data["number_of_night"]
        ) + (
            f"🔍{game_data['players'][str(self.callback.from_user.id)]['pretty_role']} "
            f"{game_data['players'][str(self.callback.from_user.id)]['url']} принял решение проверить роль {url}"
        )
        await send_a_lot_of_messages_safely(
            bot=self.callback.bot,
            text=text,
            users=game_data[Policeman.roles_key],
        )
