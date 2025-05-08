from contextlib import suppress

from cache.cache_types import GameCache, UserIdInt
from general.collection_of_roles import get_data_with_roles
from general.groupings import Groupings
from general.text import NUMBER_OF_DAY
from keyboards.inline.callback_factory.recognize_user import (
    UserActionIndexCbData,
)
from keyboards.inline.keypads.to_bot import (
    participate_in_social_life,
)
from mafia.roles import Hacker
from services.base import RouterHelper
from services.game.game_assistants import (
    get_game_data_and_user_id,
    get_game_state_by_user_state,
)
from utils.common import get_criminals_ids
from utils.informing import send_a_lot_of_messages_safely
from utils.pretty_text import make_build
from utils.state import lock_state
from utils.tg import delete_message


class UserManager(RouterHelper):
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

        await self.message.bot.send_message(
            chat_id=game_data["game_chat"],
            text=f"⚡️⚡️⚡️По слухам, {role} {url} перед смертью "
            f"проглаголил такие слова:\n\n{self.message.text}"[
                :3900
            ],
        )
        await self.message.answer(
            make_build("✅Сообщение успешно доставлено!")
        )

    @staticmethod
    def delete_user_from_waiting_for_action_at_day(
        game_data: GameCache, user_id: int
    ):
        with suppress(ValueError):
            game_data["waiting_for_action_at_day"].remove(user_id)

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
            text=f"{role} {url} передает:\n\n{self.message.text}"[
                :3900
            ],
            exclude=[self.message.from_user.id],
        )
        if (
            self.message.from_user.id in criminals_ids
            and game_data.get(Hacker.roles_key)
        ):
            await send_a_lot_of_messages_safely(
                bot=self.message.bot,
                text=f"{role} ??? передает:\n\n{self.message.text}"[
                    :3900
                ],
                users=game_data[Hacker.roles_key],
            )
        await self.message.answer(
            make_build("✅Сообщение успешно доставлено!")
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
            self.delete_user_from_waiting_for_action_at_day(
                game_data=game_data,
                user_id=self.callback.from_user.id,
            )
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
                + f"Ты выбрал голосовать за повешение {voted_url}"
            )
        )
        await self.callback.bot.send_message(
            chat_id=game_data["game_chat"],
            text=make_build(
                f"❗️{voting_url} выступает против {voted_url}!"
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
                self.delete_user_from_waiting_for_action_at_day(
                    game_data=game_data,
                    user_id=self.callback.from_user.id,
                )
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
                + "Ты решил ни за кого не голосовать"
            )
        )
        await self.callback.bot.send_message(
            chat_id=game_data["game_chat"],
            text=make_build(
                f"🦄{url} ходит с розовыми очками в мире единорогов, "
                f"эльфов и великодушных гномов, поэтому всех прощает!\n\n"
                f"Не приведет ли наивность к новым жертвам?"
            ),
            reply_markup=participate_in_social_life(),
        )
