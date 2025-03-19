import asyncio

from database.common.sessions import async_session_maker
from database.models import GroupingModel, RoleModel
from general.collection_of_roles import get_data_with_roles
from services.roles.base.roles import Groupings


async def fill_database_with_roles():
    async with async_session_maker() as session:
        groupings = [
            GroupingModel(name=grouping.value.name)
            for grouping in Groupings
        ]
        session.add_all(groupings)
        await session.flush()
        all_roles = get_data_with_roles().values()
        roles = [
            RoleModel(
                name=role.role, grouping=role.grouping.value.name
            )
            for role in all_roles
        ]
        session.add_all(roles)
        await session.commit()
