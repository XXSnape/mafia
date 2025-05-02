from collections.abc import Iterable

from cache.cache_types import OrderOfRolesCache, RolesLiteral
from database.dao.order import OrderOfRolesDAO
from database.dao.prohibited_roles import ProhibitedRolesDAO
from database.dao.settings import SettingsDao
from database.schemas.common import UserTgIdSchema
from database.schemas.roles import OrderOfRolesSchema
from general import settings
from general.collection_of_roles import (
    BASES_ROLES,
    get_data_with_roles,
)
from general.groupings import Groupings
from general.text import REQUIRE_TO_SAVE
from keyboards.inline.callback_factory.help import OrderOfRolesCbData
from keyboards.inline.keypads.order_of_roles import (
    edit_order_of_roles_kb,
    get_next_role_kb,
)
from mafia.roles import Doctor, Mafia, Policeman
from services.base import RouterHelper
from utils.pretty_text import make_build


class RoleManager(RouterHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.key = "order_of_roles"

    async def _delete_old_order_of_roles_and_add_new(
        self, roles: list[RolesLiteral]
    ):
        await self.clear_settings_data()
        dao = OrderOfRolesDAO(session=self.session)
        await dao.delete(
            UserTgIdSchema(user_tg_id=self.callback.from_user.id)
        )
        order_of_roles = [
            OrderOfRolesSchema(
                user_tg_id=self.callback.from_user.id,
                role_id=role_id,
                number=number,
            )
            for number, role_id in enumerate(roles, 1)
        ]
        await dao.add_many(order_of_roles)

    @staticmethod
    def get_current_order_text(
        selected_roles: Iterable[RolesLiteral],
        to_save: bool = True,
    ):
        all_roles = get_data_with_roles()
        result = "ℹ️Текущий порядок ролей:\n\n"
        if not selected_roles:
            selected_roles = BASES_ROLES
        for index, role in enumerate(selected_roles, 1):
            result += (
                f"{index}) {all_roles[role].role}"
                f"{all_roles[role].grouping.value.name[-1]}\n"
            )
        if (
            to_save
            and len(selected_roles)
            > settings.mafia.minimum_number_of_players
        ):
            result += f"\n\n{REQUIRE_TO_SAVE}"
        return make_build(result)

    async def view_order_of_roles(self):
        dao = OrderOfRolesDAO(session=self.session)
        order_of_roles = await dao.get_roles_ids_of_order_of_roles(
            UserTgIdSchema(user_tg_id=self.callback.from_user.id),
        )
        text = self.get_current_order_text(
            order_of_roles, to_save=False
        )
        await self.clear_settings_data()
        await self.callback.message.edit_text(
            text=make_build(text),
            reply_markup=edit_order_of_roles_kb(
                order_of_roles != list(BASES_ROLES)
            ),
        )

    async def start_editing_order(self):
        attacking = []
        other = []
        user_schema = UserTgIdSchema(
            user_tg_id=self.callback.from_user.id
        )
        banned_roles_ids = await ProhibitedRolesDAO(
            session=self.session
        ).get_roles_ids_of_banned_roles(user_schema)
        criminal_every_3 = await SettingsDao(
            session=self.session
        ).get_every_3_attr(user_schema)
        all_roles = get_data_with_roles()
        for role_id, role in all_roles.items():
            if role_id not in banned_roles_ids and role_id not in {
                Mafia.role_id,
                Doctor.role_id,
                Policeman.role_id,
            }:
                if role.grouping != Groupings.criminals:
                    other.append(role_id)
                else:
                    attacking.append(role_id)
        selected = list(BASES_ROLES)
        order_data: OrderOfRolesCache = {
            "attacking": attacking,
            "other": other,
            "selected": selected,
            "criminal_every_3": criminal_every_3,
        }
        await self.set_settings_data(order_data)
        markup = get_next_role_kb(order_data=order_data)
        await self.callback.message.edit_text(
            text=self.get_current_order_text(selected),
            reply_markup=markup,
        )

    async def add_new_role_to_queue(
        self, callback_data: OrderOfRolesCbData
    ):
        order_data: OrderOfRolesCache = (
            await self.get_settings_data()
        )
        role = get_data_with_roles(callback_data.role_id)
        key = (
            "attacking"
            if role.grouping == Groupings.criminals
            else "other"
        )
        if role.there_may_be_several is False:
            order_data[key].remove(callback_data.role_id)
        order_data["selected"].append(callback_data.role_id)
        if (
            len(order_data["selected"])
            == settings.mafia.maximum_number_of_players
        ):
            await self.callback.answer(
                f"Пока в игре могут участвовать "
                f"только {settings.mafia.maximum_number_of_players} человек!",
                show_alert=True,
            )
            await self._delete_old_order_of_roles_and_add_new(
                roles=order_data["selected"]
            )
            await self.view_order_of_roles()
            return
        markup = get_next_role_kb(order_data=order_data)
        await self.set_settings_data(order_data)
        await self.callback.message.edit_text(
            text=self.get_current_order_text(order_data["selected"]),
            reply_markup=markup,
        )

    async def pop_latest_role_in_order(self):
        order_data: OrderOfRolesCache = (
            await self.get_settings_data()
        )
        selected = order_data["selected"]
        latest_role_key = selected.pop()
        role = get_data_with_roles(latest_role_key)
        key = (
            "attacking"
            if role.grouping == Groupings.criminals
            else "other"
        )
        if latest_role_key not in order_data[key]:
            order_data[key].append(latest_role_key)
        markup = get_next_role_kb(
            order_data=order_data, automatic_attacking=False
        )
        await self.set_settings_data(order_data)
        await self.callback.message.edit_text(
            text=self.get_current_order_text(order_data["selected"]),
            reply_markup=markup,
        )

    async def save_order_of_roles(self):
        order_data: OrderOfRolesCache = (
            await self.get_settings_data()
        )
        selected = order_data["selected"]
        await self._delete_old_order_of_roles_and_add_new(
            roles=selected
        )
        await self.callback.answer(
            "✅Порядок ролей успешно сохранён!", show_alert=True
        )
        await self.view_order_of_roles()

    async def clear_order_of_roles(self):
        dao = OrderOfRolesDAO(session=self.session)
        await dao.delete(
            UserTgIdSchema(user_tg_id=self.callback.from_user.id)
        )
        await self.callback.answer(
            "✅Порядок ролей сброшен!", show_alert=True
        )
        await self.view_order_of_roles()
