from database.dao.base import BaseDAO
from database.models import GroupModel
from database.schemas.common import UserTgIdSchema
from sqlalchemy import select


class SettingsDao(BaseDAO[GroupModel]):
    model = GroupModel

    async def get_every_3_attr(
        self, user_tg_id: UserTgIdSchema
    ) -> bool:
        query = select(self.model.mafia_every_3).filter_by(
            **user_tg_id.model_dump()
        )
        return await self._session.scalar(query)
