import asyncio

from database.common.sessions import async_session_maker
from database.models import GroupingModel, RoleModel
from general.collection_of_roles import get_data_with_roles

Groupings


async def fill_database_with_roles():
    async with async_session_maker() as session:
        groupings = [
            GroupingModel(name=grouping.value.name)
            for grouping in Groupings
        ]
        session.add_all(groupings)
        await session.flush()
        all_roles = get_data_with_roles()
        roles = [
            RoleModel(
                name=role.role,
                key=key,
                grouping=role.grouping.value.name,
            )
            for key, role in all_roles.items()
        ]
        session.add_all(roles)
        await session.commit()


if __name__ == "__main__":
    asyncio.run(fill_database_with_roles())
