from pydantic import BaseModel

from database.dao.repositories.base import BaseDAO
from database.models import ProhibitedRoleModel


class ProhibitedRoleSchema(BaseModel):
    user_tg_id: int
    role: str | None = None


class ProhibitedRolesDAO(BaseDAO[ProhibitedRoleModel]):
    model = ProhibitedRoleModel

    async def save_new_prohibited_roles(
        self, user_id: int, roles: list[str] | None
    ):
        await self.delete(ProhibitedRoleSchema(user_tg_id=user_id))
        if roles:
            prohibited_roles = [
                ProhibitedRoleSchema(user_tg_id=user_id, role=role)
                for role in roles
            ]
            await self.add_many(prohibited_roles)

    async def get_banned_roles(self, user_id: int):
        result = await self.find_all(
            ProhibitedRoleSchema(user_tg_id=user_id)
        )
        if result:
            return (
                "Забаненные роли:\n"
                + "\n".join(record.role for record in result),
                True,
            )
        return "Все роли могут участвовать в игре!", False
