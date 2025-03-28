import asyncio

from constants.output import NUMBER_OF_NIGHT, ROLE_IS_KNOWN
from general.collection_of_roles import get_data_with_roles
from keyboards.inline.buttons.common import BACK_BTN
from keyboards.inline.callback_factory.recognize_user import (
    UserActionIndexCbData,
    PoliceActionIndexCbData,
    police_kill_cb_data,
    police_check_cb_data,
)
from keyboards.inline.cb.cb_text import (
    POLICEMAN_KILLS_CB,
    POLICEMAN_CHECKS_CB,
)
from keyboards.inline.keypads.mailing import (
    choose_fake_role_kb,
    send_selection_to_players_kb,
    kill_or_poison_kb,
    kill_or_check_on_policeman,
)
from services.base import RouterHelper
from services.game.actions_at_night import (
    get_game_state_and_data,
    get_game_state_data_and_user_id,
    save_notification_message,
    trace_all_actions,
    take_action_and_register_user,
)
from services.game.roles import (
    Analyst,
    Policeman,
    PolicemanAlias,
    Forger,
    Instigator,
    Poisoner,
)
from states.states import UserFsm
from utils.tg import delete_message
from utils.utils import make_pretty


class AnalystSaver(RouterHelper):
    async def analyst_assumes_draw(self):
        game_state, game_data = await get_game_state_and_data(
            tg_obj=self.callback,
            state=self.state,
            dispatcher=self.dispatcher,
        )
        game_data[Analyst.processed_users_key].append(0)
        await delete_message(self.callback.message)
        await self.callback.message.answer(
            text=NUMBER_OF_NIGHT.format(game_data["number_of_night"])
            + "Ты предположил, что никого не повесят днём"
        )
        await self.callback.bot.send_message(
            chat_id=game_data["game_chat"],
            text=Analyst.message_to_group_after_action,
        )
        await game_state.set_data(game_data)


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
        game_data[Forger.extra_data[0].key].append([user_id])
        all_roles = get_data_with_roles()
        current_roles = [
            (all_roles[data["enum_name"]].role, data["enum_name"])
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
        game_data[Forger.extra_data[0].key].clear()
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
        forger_roles_key = Forger.extra_data[0].key
        game_data[forger_roles_key][0].append(self.callback.data)
        user_id = game_data[forger_roles_key][0][0]
        trace_all_actions(
            callback=self.callback,
            game_data=game_data,
            user_id=user_id,
        )
        save_notification_message(
            game_data=game_data,
            processed_user_id=user_id,
            message=Forger.notification_message,
            current_user_id=self.callback.from_user.id,
        )
        url = game_data["players"][str(user_id)]["url"]
        await delete_message(self.callback.message)
        await game_state.set_data(game_data)
        await self.callback.bot.send_message(
            chat_id=game_data["game_chat"],
            text=Forger.message_to_group_after_action,
        )
        await self.callback.message.answer(
            text=NUMBER_OF_NIGHT.format(game_data["number_of_night"])
            + f"Ты выбрал подменить документы {url} на {pretty_role}"
        )


class InstigatorSaver(RouterHelper):
    async def instigator_chooses_subject(
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
        game_data[Instigator.extra_data[0].key].append([user_id])
        markup = send_selection_to_players_kb(
            players_ids=game_data["players_ids"],
            players=game_data["players"],
            extra_buttons=(BACK_BTN,),
            exclude=user_id,
        )
        await self.state.set_state(UserFsm.INSTIGATOR_CHOOSES_OBJECT)
        await game_state.set_data(game_data)
        await self.callback.message.edit_text(
            text=f"За кого должен проголосовать {url}?",
            reply_markup=markup,
        )

    async def instigator_cancels_selection(self):
        game_state, game_data = await get_game_state_and_data(
            tg_obj=self.callback,
            state=self.state,
            dispatcher=self.dispatcher,
        )
        await self.state.set_state(
            UserFsm.INSTIGATOR_CHOOSES_SUBJECT
        )
        instigator = Instigator()
        game_data[Instigator.extra_data[0].key].clear()
        await game_state.set_data(game_data)
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
        game_state, game_data, user_id = (
            await take_action_and_register_user(
                callback=self.callback,
                callback_data=callback_data,
                state=self.state,
                dispatcher=self.dispatcher,
            )
        )
        deceived_user = game_data[Instigator.extra_data[0].key][0]
        deceived_user.append(user_id)
        subject_url = game_data["players"][str(deceived_user[0])][
            "url"
        ]
        object_id = game_data["players"][str(deceived_user[1])][
            "url"
        ]
        await delete_message(self.callback.message)
        await game_state.set_data(game_data)
        await self.callback.message.answer(
            text=f"Днём {subject_url} проголосует за {object_id}, если попытается голосовать"
        )


class PoisonerSaver(RouterHelper):
    async def poisoner_chose_to_kill(self):
        game_state, game_data = await get_game_state_and_data(
            tg_obj=self.callback,
            state=self.state,
            dispatcher=self.dispatcher,
        )
        poisoned = game_data[Poisoner.extra_data[0].key]
        poisoned[1] = 1
        await delete_message(self.callback.message)
        await game_state.set_data(game_data)
        await self.callback.message.answer(
            text=NUMBER_OF_NIGHT.format(game_data["number_of_night"])
            + "Ты решил всех убить!"
        )

    async def poisoner_poisons(self):
        game_state, game_data = await get_game_state_and_data(
            tg_obj=self.callback,
            state=self.state,
            dispatcher=self.dispatcher,
        )
        poisoned = game_data[Poisoner.extra_data[0].key]
        exclude = (poisoned[0] if poisoned else []) + [
            self.callback.from_user.id
        ]
        await self.state.set_state(UserFsm.POISONER_CHOSE_TO_KILL)
        await self.callback.message.edit_text(
            "Кого собираешься отравить?",
            reply_markup=send_selection_to_players_kb(
                players_ids=game_data["players_ids"],
                players=game_data["players"],
                extra_buttons=(BACK_BTN,),
                exclude=exclude,
            ),
        )

    async def poisoner_cancels_selection(self):
        _, game_data = await get_game_state_and_data(
            tg_obj=self.callback,
            state=self.state,
            dispatcher=self.dispatcher,
        )
        poisoned = game_data[Poisoner.extra_data[0].key]
        await self.state.set_state(UserFsm.POISONER_CHOOSES_ACTION)
        await self.callback.message.edit_text(
            text=Poisoner.mail_message,
            reply_markup=kill_or_poison_kb(poisoned=poisoned),
        )

    async def poisoner_chose_victim(
        self, callback_data: UserActionIndexCbData
    ):
        game_state, game_data, user_id = (
            await take_action_and_register_user(
                callback=self.callback,
                callback_data=callback_data,
                state=self.state,
                dispatcher=self.dispatcher,
            )
        )
        poisoned = game_data[Poisoner.extra_data[0].key]
        if poisoned:
            poisoned[0].append(user_id)
        else:
            poisoned[:] = [[user_id], 0]
        await game_state.set_data(game_data)


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
            players_ids=game_data["players_ids"],
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
        await take_action_and_register_user(
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
            "enum_name"
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
