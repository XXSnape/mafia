from constants.output import NUMBER_OF_NIGHT
from general.collection_of_roles import get_data_with_roles
from keyboards.inline.callback_factory.recognize_user import (
    UserActionIndexCbData,
)
from keyboards.inline.keypads.mailing import choose_fake_role_kb
from services.base import RouterHelper
from services.game.actions_at_night import (
    get_game_state_data_and_user_id,
    get_game_state_and_data,
    trace_all_actions,
)
from mafia.roles import Forger, Policeman, PolicemanAlias
from utils.tg import delete_message
from utils.pretty_text import make_pretty, make_build


class ForgerSaver(RouterHelper):
    async def forger_fakes(
        self, callback_data: UserActionIndexCbData
    ):
        game_state, game_data, user_id = (
            await get_game_state_data_and_user_id(
                callback=self.callback,
                callback_data=callback_data,
                state=self.state,
                dispatcher=self.dispatcher,
            )
        )
        url = game_data["players"][str(user_id)]["url"]
        game_data["forged_roles"].append(user_id)
        all_roles = get_data_with_roles()
        current_roles = [
            (all_roles[data["role_id"]].role, data["role_id"])
            for _, data in game_data["players"].items()
            if data["role"]
            not in (Policeman.role, PolicemanAlias.role)
        ]
        markup = choose_fake_role_kb(current_roles)
        await game_state.set_data(game_data)
        await self.callback.message.edit_text(
            text=f"Выбери для {url} новую роль", reply_markup=markup
        )

    async def forges_cancels_selection(self):
        game_state, game_data = await get_game_state_and_data(
            tg_obj=self.callback,
            state=self.state,
            dispatcher=self.dispatcher,
        )
        game_data["forged_roles"].clear()
        markup = Forger().generate_markup(
            player_id=self.callback.from_user.id, game_data=game_data
        )
        await game_state.set_data(game_data)
        await self.callback.message.edit_text(
            text=Forger.mail_message,
            reply_markup=markup,
        )

    async def forges_selects_documents(self):
        game_state, game_data = await get_game_state_and_data(
            tg_obj=self.callback,
            state=self.state,
            dispatcher=self.dispatcher,
        )
        current_role = get_data_with_roles(self.callback.data)
        pretty_role = make_pretty(current_role.role)
        forger_roles_key = "forged_roles"
        game_data[forger_roles_key].append(self.callback.data)
        user_id = game_data[forger_roles_key][0]
        url = game_data["players"][str(user_id)]["url"]
        await trace_all_actions(
            callback=self.callback,
            game_data=game_data,
            user_id=user_id,
            current_role=Forger(),
            message_to_user=f"Ты выбрал подменить документы {url} на {pretty_role}",
        )
        await game_state.set_data(game_data)
