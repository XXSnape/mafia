from database.dao.base import BaseDAO
from database.models import GroupModel


class GroupsDao(BaseDAO[GroupModel]):
    model = GroupModel
