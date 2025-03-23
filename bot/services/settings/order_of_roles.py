from cache.cache_types import OrderOfRolesCache
from database.dao.order import OrderOfRolesDAO
from database.schemas.roles import UserTgId, OrderOfRolesSchema
from general.collection_of_roles import (
    get_data_with_roles,
    BASES_ROLES,
)
from general.groupings import Groupings
from keyboards.inline.keypads.settings import (
    edit_roles_kb,
    get_next_role_kb,
)

from services.base import RouterHelper
from states.settings import SettingsFsm
from utils.utils import make_build


class RoleManager(RouterHelper):
    CURRENT_ORDER_OF_ROLES = make_build(
        "ℹ️Текущий порядок ролей:\n\n"
    )

    async def _delete_old_order_of_roles_and_add_new(
        self, roles: list[str]
    ):
        await self.state.set_data({})
        dao = OrderOfRolesDAO(session=self.session)
        await dao.delete(
            UserTgId(user_tg_id=self.callback.from_user.id)
        )
        all_roles = get_data_with_roles()
        order_of_roles = [
            OrderOfRolesSchema(
                user_tg_id=self.callback.from_user.id,
                role=all_roles[role].role,
                number=number,
            )
            for number, role in enumerate(roles, 1)
        ]
        await dao.add_many(order_of_roles)

    @classmethod
    def get_current_order_text(
        cls, selected_roles: list[str], to_save: bool = True
    ):
        all_roles = get_data_with_roles()
        result = cls.CURRENT_ORDER_OF_ROLES
        if not selected_roles:
            selected_roles = BASES_ROLES
        if to_save and len(selected_roles) > 4:
            result = cls.REQUIRE_TO_SAVE + result
        for index, role in enumerate(selected_roles, 1):
            result += f"{index}) {all_roles[role].role}\n"
        return result

    async def view_order_of_roles(self):
        dao = OrderOfRolesDAO(session=self.session)
        order_of_roles = await dao.find_all(
            UserTgId(user_tg_id=self.callback.from_user.id),
            sort_fields=["number"],
        )
        text = self.CURRENT_ORDER_OF_ROLES
        if not order_of_roles:
            text = self.get_current_order_text(BASES_ROLES)
        else:
            for record in order_of_roles:
                text += f"{record.number}) {record.role}\n"
        await self.state.clear()
        await self.state.set_state(SettingsFsm.ORDER_OF_ROLES)
        await self.callback.message.edit_text(
            text=text,
            reply_markup=edit_roles_kb(bool(order_of_roles)),
        )

    async def start_editing_order(self):
        attacking = []
        other = []
        banned_roles = await self._get_banned_roles()
        all_roles = get_data_with_roles()
        for key, role in all_roles.items():
            if role.role not in banned_roles and key not in [
                "don",
                "doctor",
                "policeman",
            ]:
                if role.grouping != Groupings.criminals:
                    other.append(key)
                else:
                    attacking.append(key)
        selected = BASES_ROLES.copy()
        order_data: OrderOfRolesCache = {
            "attacking": attacking,
            "other": other,
            "selected": selected,
        }
        await self.state.set_state(SettingsFsm.ORDER_OF_ROLES)
        await self.state.set_data(order_data)
        markup = get_next_role_kb(order_data=order_data)
        await self.callback.message.edit_text(
            text=self.get_current_order_text(selected),
            reply_markup=markup,
        )

    async def add_new_role_to_queue(self):
        order_data: OrderOfRolesCache = await self.state.get_data()
        role = get_data_with_roles(self.callback.data)
        key = (
            "attacking"
            if role.grouping == Groupings.criminals
            else "other"
        )
        if role.there_may_be_several is False:
            order_data[key].remove(self.callback.data)
        order_data["selected"].append(self.callback.data)
        if len(order_data["selected"]) == 30:
            await self.callback.answer(
                "Пока можно выбрать только 30 ролей!",
                show_alert=True,
            )
            await self._delete_old_order_of_roles_and_add_new(
                roles=order_data["selected"]
            )
            await self.view_order_of_roles()
            return
        markup = get_next_role_kb(order_data=order_data)
        await self.state.set_data(order_data)
        await self.callback.message.edit_text(
            text=self.get_current_order_text(order_data["selected"]),
            reply_markup=markup,
        )

    async def pop_latest_role_in_order(self):
        order_data: OrderOfRolesCache = await self.state.get_data()
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
        await self.state.set_data(order_data)
        await self.callback.message.edit_text(
            text=self.get_current_order_text(order_data["selected"]),
            reply_markup=markup,
        )

    async def save_order_of_roles(self):
        order_data: OrderOfRolesCache = await self.state.get_data()
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
            UserTgId(user_tg_id=self.callback.from_user.id)
        )
        await self.callback.answer(
            "✅Порядок ролей сброшен!", show_alert=True
        )
        await self.view_order_of_roles()
