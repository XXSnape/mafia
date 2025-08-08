from html import escape

import sqlalchemy
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from cache.cache_types import (
    GameCache,
    UserIdInt,
)
from database.dao.users import UsersDao
from database.schemas.assets import NumberOfAssetsSchema
from database.schemas.common import TgIdSchema
from general import settings
from general.collection_of_roles import get_data_with_roles
from general.commands import PrivateCommands
from general.groupings import Groupings
from general.text import DOUBLE_VOICE, NUMBER_OF_DAY, NUMBER_OF_NIGHT
from keyboards.inline.callback_factory.recognize_user import (
    UserActionIndexCbData,
)
from keyboards.inline.keypads.shop import to_shop_kb
from keyboards.inline.keypads.to_bot import (
    participate_in_social_life,
)
from services.base import RouterHelper
from services.game.game_assistants import (
    get_game_data_and_user_id,
    get_game_state_by_user_state,
)
from states.game import GameFsm
from utils.common import (
    get_criminals_ids,
    remove_from_expected_at_day,
    remove_from_expected_at_night,
)
from utils.informing import (
    get_profiles,
    send_a_lot_of_messages_safely,
)
from utils.pretty_text import make_build
from utils.state import lock_state
from utils.tg import delete_message, resending_message

from mafia.roles import Hacker, Manager


class UserManager(RouterHelper):

    async def _check_running_game(
        self, if_not_in_game_message: str, if_not_alive_message: str
    ) -> tuple[FSMContext, GameCache] | None:
        try:
            game_state = await get_game_state_by_user_state(
                tg_obj=self.message,
                user_state=self.state,
                dispatcher=self.dispatcher,
            )
        except KeyError:
            await self.message.reply(
                text=make_build(if_not_in_game_message)
            )
            return None
        state = await game_state.get_state()
        if state != GameFsm.STARTED.state:
            await self.message.reply(
                text=make_build("Игра еще не началась!")
            )
            return None
        game_data: GameCache = await game_state.get_data()
        if (
            self.message.from_user.id
            not in game_data["live_players_ids"]
        ):
            await self.message.reply(
                text=make_build(if_not_alive_message)
            )
            return None
        return game_state, game_data

    async def refuse_move(self):
        await delete_message(
            message=self.callback.message, raise_exception=True
        )
        game_state = await get_game_state_by_user_state(
            tg_obj=self.callback,
            user_state=self.state,
            dispatcher=self.dispatcher,
        )
        async with lock_state(game_state):
            game_data: GameCache = await game_state.get_data()
            remove_from_expected_at_night(
                callback=self.callback, game_data=game_data
            )
            await game_state.set_data(game_data)
        await self.callback.message.answer(
            make_build(
                NUMBER_OF_NIGHT.format(game_data["number_of_night"])
                + "Ты отказался делать свой ход."
            )
        )

    async def send_latest_message(self):
        game_state = await get_game_state_by_user_state(
            tg_obj=self.message,
            user_state=self.state,
            dispatcher=self.dispatcher,
        )
        await self.state.clear()
        game_data: GameCache = await game_state.get_data()
        role = (
            game_data["players"][str(self.message.from_user.id)][
                "pretty_role"
            ]
            if game_data["settings"]["show_roles_after_death"]
            else "???"
        )
        url = game_data["players"][str(self.message.from_user.id)][
            "url"
        ]
        await resending_message(
            bot=self.message.bot,
            chat_id=game_data["game_chat"],
            text=f"⚡️⚡️⚡️По слухам, {role} {url} перед смертью "
            f"проглаголил такие слова:\n\n{escape(self.message.text)}"[
                : settings.mafia.number_of_characters_in_message
            ],
        )
        await self.message.reply(
            make_build("✅Сообщение успешно доставлено!"),
            protect_content=game_data["settings"]["protect_content"],
        )

    async def send_anonymously_to_group(
        self, command: CommandObject
    ):
        anonym_message = command.args
        if not anonym_message:
            await self.message.reply(
                text=make_build(
                    "Некорректная форма отправки анонимного сообщения, пример:\n\n"
                )
                + f"/{PrivateCommands.anon.name} Всем хорошей игры!"
            )
            return
        result = await self._check_running_game(
            if_not_in_game_message="Анонимные сообщения можно отправлять только во время игры",
            if_not_alive_message="Отправлять сообщения анонимно можно только будучи в игре!",
        )
        if result is None:
            return
        _, game_data = result
        user_id = self.message.from_user.id
        user_tg_id = TgIdSchema(tg_id=user_id)
        await self.session.connection(
            execution_options={"isolation_level": "SERIALIZABLE"}
        )
        users_dao = UsersDao(session=self.session)
        user = await users_dao.get_user_or_create(user_tg_id)
        if user.anonymous_letters < 1:
            await self.message.reply(
                text=make_build("Нет анонимок! Купи их в магазине!"),
                reply_markup=to_shop_kb(),
            )
            return
        try:
            await users_dao.update(
                filters=user_tg_id,
                values=NumberOfAssetsSchema(
                    anonymous_letters=user.anonymous_letters - 1
                ),
            )
            await resending_message(
                bot=self.message.bot,
                chat_id=game_data["game_chat"],
                text=f"😱😱😱НЕИЗВЕСТНЫЙ ОТПРАВИТЕЛЬ\n\n{escape(anonym_message)}"[
                    : settings.mafia.number_of_characters_in_message
                ],
            )
        except sqlalchemy.exc.DBAPIError:
            await self.message.reply(
                make_build("Попробуй еще раз😉")
            )
            return
        except TelegramAPIError:
            await users_dao.update(
                filters=user_tg_id,
                values=NumberOfAssetsSchema(
                    anonymous_letters=user.anonymous_letters + 1
                ),
            )
            await self.message.reply(
                make_build(
                    "Не можем связаться с группой, попробуй еще раз..."
                )
            )
            return

        await self.message.reply(
            make_build(
                f"✅Анонимное сообщение успешно доставлено, "
                f"осталось анонимок: {user.anonymous_letters}"
            ),
            reply_markup=to_shop_kb(),
        )

    async def allies_communicate(self):
        game_state = await get_game_state_by_user_state(
            tg_obj=self.message,
            user_state=self.state,
            dispatcher=self.dispatcher,
        )
        game_data: GameCache = await game_state.get_data()
        current_role = get_data_with_roles(
            game_data["players"][str(self.message.from_user.id)][
                "role_id"
            ]
        )
        if (
            current_role.grouping != Groupings.criminals
            and game_data["settings"]["show_peaceful_allies"]
            is False
        ):
            return

        url = game_data["players"][str(self.message.from_user.id)][
            "url"
        ]
        role = game_data["players"][str(self.message.from_user.id)][
            "pretty_role"
        ]
        criminals_ids = get_criminals_ids(game_data)
        if current_role.grouping == Groupings.criminals:
            aliases = criminals_ids
        else:
            aliases = game_data[current_role.roles_key]
        if len(aliases) == 1:
            return
        await send_a_lot_of_messages_safely(
            bot=self.message.bot,
            users=aliases,
            text=f"{role} {url} передает:\n\n{escape(self.message.text)}"[
                : settings.mafia.number_of_characters_in_message
            ],
            exclude=[self.message.from_user.id],
            protect_content=game_data["settings"]["protect_content"],
        )
        if (
            self.message.from_user.id in criminals_ids
            and game_data.get(Hacker.roles_key)
        ):
            await send_a_lot_of_messages_safely(
                bot=self.message.bot,
                text=f"{role} ??? передает:\n\n{escape(self.message.text)}"[
                    : settings.mafia.number_of_characters_in_message
                ],
                users=game_data[Hacker.roles_key],
                protect_content=game_data["settings"][
                    "protect_content"
                ],
            )
        await self.message.reply(
            make_build("✅Сообщение успешно доставлено!"),
            protect_content=game_data["settings"]["protect_content"],
        )

    def check_for_cheating(
        self, game_data: GameCache
    ) -> UserIdInt | None:
        deceived_user = game_data.get("deceived", [])
        if (
            len(deceived_user) == 2
            and self.callback.from_user.id == deceived_user[0]
            and deceived_user[1] in game_data["live_players_ids"]
        ):
            return deceived_user[1]
        return None

    def _get_repeat_and_text(
        self, game_data: GameCache
    ) -> tuple[int, str]:
        if (
            Manager().get_processed_user_id(game_data=game_data)
            == self.callback.from_user.id
        ):
            return 2, DOUBLE_VOICE + "\n\n"
        return 1, ""

    async def vote_for(
        self, callback_data: UserActionIndexCbData | None
    ):
        if callback_data is not None:
            await delete_message(
                self.callback.message, raise_exception=True
            )
        game_state = await get_game_state_by_user_state(
            tg_obj=self.callback,
            user_state=self.state,
            dispatcher=self.dispatcher,
        )
        async with lock_state(game_state):
            if callback_data is None:
                game_data: GameCache = await game_state.get_data()
                voted_user_id = self.check_for_cheating(game_data)
            else:
                game_data, voted_user_id = (
                    await get_game_data_and_user_id(
                        game_state=game_state,
                        callback_data=callback_data,
                    )
                )
                voted_user_id = (
                    self.check_for_cheating(game_data)
                    or voted_user_id
                )
            if (
                self.callback.from_user.id
                not in game_data["waiting_for_action_at_day"]
            ):
                return
            remove_from_expected_at_day(
                game_data=game_data, callback=self.callback
            )
            repeat, text = self._get_repeat_and_text(
                game_data=game_data
            )
            for _ in range(repeat):
                game_data["vote_for"].append(
                    [self.callback.from_user.id, voted_user_id]
                )
            await game_state.set_data(game_data)
        voting_url = (
            game_data["players"][str(self.callback.from_user.id)][
                "url"
            ]
            if game_data["settings"]["show_usernames_during_voting"]
            else "???"
        )
        voted_url = game_data["players"][str(voted_user_id)]["url"]
        await self.callback.message.answer(
            make_build(
                NUMBER_OF_DAY.format(game_data["number_of_night"])
                + f"{text}Ты выбрал голосовать за повешение {voted_url}"
            ),
            protect_content=game_data["settings"]["protect_content"],
        )
        await self.callback.bot.send_message(
            chat_id=game_data["game_chat"],
            text=make_build(
                f"{text}❗️{voting_url} выступает против {voted_url}!"
            ),
            reply_markup=participate_in_social_life(),
        )

    async def dont_vote_for_anyone(self):
        await delete_message(
            self.callback.message, raise_exception=True
        )
        game_state = await get_game_state_by_user_state(
            tg_obj=self.callback,
            user_state=self.state,
            dispatcher=self.dispatcher,
        )
        is_deceived: bool = False
        async with lock_state(game_state):
            game_data: GameCache = await game_state.get_data()
            if self.check_for_cheating(game_data):
                is_deceived = True
            else:
                if (
                    self.callback.from_user.id
                    not in game_data["waiting_for_action_at_day"]
                ):
                    return
                remove_from_expected_at_day(
                    game_data=game_data, callback=self.callback
                )
                repeat, text = self._get_repeat_and_text(
                    game_data=game_data
                )
                for _ in range(repeat):
                    game_data["refused_to_vote"].append(
                        self.callback.from_user.id
                    )
                await game_state.set_data(game_data)
        if is_deceived:
            await self.vote_for(callback_data=None)
            return
        url = (
            game_data["players"][str(self.callback.from_user.id)][
                "url"
            ]
            if game_data["settings"]["show_usernames_during_voting"]
            else "???"
        )
        await self.callback.message.answer(
            make_build(
                NUMBER_OF_DAY.format(game_data["number_of_night"])
                + f"{text}Ты решил ни за кого не голосовать"
            ),
            protect_content=game_data["settings"]["protect_content"],
        )
        await self.callback.bot.send_message(
            chat_id=game_data["game_chat"],
            text=make_build(
                f"{text}🦄{url} ходит с розовыми очками в мире единорогов, "
                f"эльфов и великодушных гномов, поэтому всех прощает!\n\n"
                f"Не приведет ли наивность к новым жертвам?"
            ),
            reply_markup=participate_in_social_life(),
        )

    async def want_to_leave_game(self):
        result = await self._check_running_game(
            if_not_in_game_message="Команда работает только во время игры!",
            if_not_alive_message="Ты не в игре!",
        )
        if result is None:
            return
        game_state, _ = result
        user_id = self.message.from_user.id
        async with lock_state(game_state):
            game_data: GameCache = await game_state.get_data()
            if user_id in game_data["wish_to_leave_game"]:
                await self.message.reply(
                    make_build(
                        "Ты уже в списках с желающими покинуть игру"
                    )
                )
                return
            game_data["wish_to_leave_game"] = [
                wish_to_leave_id
                for wish_to_leave_id in game_data[
                    "wish_to_leave_game"
                ]
                if wish_to_leave_id in game_data["live_players_ids"]
            ] + [user_id]
            await game_state.set_data(game_data)
        users = get_profiles(
            players_ids=game_data["wish_to_leave_game"],
            players=game_data["players"],
            sorting_factory=None,
        )
        number_of_people_to_leave = len(
            game_data["wish_to_leave_game"]
        )
        total_number_of_players = len(game_data["live_players_ids"])
        text = (
            f"❗️Игроки, желающие завершить игру досрочно "
            f"({number_of_people_to_leave} из {total_number_of_players}):\n{users}"
        )
        if number_of_people_to_leave == total_number_of_players:
            text += "\n\n🏁Игра скоро завершится"
        await resending_message(
            bot=self.message.bot,
            chat_id=game_data["game_chat"],
            text=make_build(text),
        )
        await self.message.reply(
            make_build("😐Твое желание покинуть игру учтено")
        )
