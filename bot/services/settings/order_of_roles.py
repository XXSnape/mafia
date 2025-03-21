from cache.cache_types import OrderOfRolesCache
from database.dao.order import OrderOfRolesDAO
from database.schemas.roles import UserTgId
from general.collection_of_roles import get_data_with_roles
from general.groupings import Groupings
from keyboards.inline.keypads.settings import (
    edit_roles_kb,
    get_next_role_kb,
)

from services.game import roles
from services.settings.base import RouterHelper
from states.settings import SettingsFsm


class RoleManager(RouterHelper):
    @staticmethod
    def _get_current_order(selected_roles: list[str]):
        all_roles = get_data_with_roles()
        result = "Текущий порядок ролей:\n\n"
        for index, role in enumerate(selected_roles, 1):
            result += f"{index}) {all_roles[role].role}\n"
        return result

    async def view_order_of_roles(self):
        dao = OrderOfRolesDAO(session=self.session)
        order_of_roles = await dao.find_all(
            UserTgId(user_tg_id=self.callback.from_user.id),
            sort_fields=["number"],
        )
        text = "Текущий порядок ролей:\n\n"
        if not order_of_roles:
            bases = [
                roles.Mafia(),
                roles.Doctor(),
                roles.Policeman(),
                roles.Civilian(),
            ]
            for num, role in enumerate(bases, 1):
                text += f"{num}) {role.role}\n"
        else:
            for record in order_of_roles:
                text += f"{record.number}) {record.role}\n"
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
        selected = [
            "don",
            "doctor",
            "policeman",
            "civilian",
        ]
        order_data: OrderOfRolesCache = {
            "attacking": attacking,
            "other": other,
            "selected": selected,
        }
        await self.state.set_state(SettingsFsm.ORDER_OF_ROLES)
        await self.state.set_data(order_data)
        markup = get_next_role_kb(order_data=order_data)
        await self.callback.message.edit_text(
            text=self._get_current_order(selected),
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
            dao = OrderOfRolesDAO(session=self.session)
            await dao.save_order_of_roles(
                user_id=self.callback.from_user.id,
                roles=order_data["selected"],
            )
            await self.callback.message.edit_text(
                text=self._get_current_order(order_data["selected"])
            ),
            await self.state.clear()
            return
        markup = get_next_role_kb(order_data=order_data)
        await self.state.set_data(order_data)
        await self.callback.message.edit_text(
            text=self._get_current_order(order_data["selected"]),
            reply_markup=markup,
        )

    async def save_order_of_roles(self):
        order_data: OrderOfRolesCache = await self.state.get_data()
        selected = order_data["selected"]
        text = self._get_current_order(selected)
        dao = OrderOfRolesDAO(session=self.session)
        await dao.save_order_of_roles(
            user_id=self.callback.from_user.id,
            roles=order_data["selected"],
        )
        await self.state.clear()
        await self.callback.answer(
            "Порядок ролей успешно сохранён!", show_alert=True
        )
        await self.callback.message.edit_text(text=text)
        await self.callback.message.answer("/settings - настройки")
