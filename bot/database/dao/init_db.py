from database.common.sessions import async_session_maker
from database.models import AssetModel, GroupingModel, RoleModel
from general import settings
from general.collection_of_roles import get_data_with_roles
from general.groupings import Groupings
from general.resources import Resources, get_data_about_resource
from loguru import logger
from sqlalchemy.exc import DatabaseError


async def fill_database_with_roles():
    if settings.mafia.init_db is False:
        return
    try:
        async with async_session_maker() as session:
            groupings = [
                GroupingModel(name=grouping.value.name)
                for grouping in Groupings
            ]
            session.add_all(groupings)
            all_roles = get_data_with_roles()
            roles = [
                RoleModel(
                    key=key,
                    grouping=role.grouping.value.name,
                )
                for key, role in all_roles.items()
            ]
            session.add_all(roles)
            assets = [
                AssetModel(
                    name=resource,
                    cost=get_data_about_resource(resource).cost,
                )
                for resource in Resources
            ]
            session.add_all(assets)
            await session.commit()
    except DatabaseError:
        await session.rollback()
        logger.exception("Ошибка при инициализации ролей")
