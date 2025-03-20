from database.dao.base import BaseDAO
from database.models import ProhibitedRoleModel


class ProhibitedRolesDAO(BaseDAO[ProhibitedRoleModel]):
    model = ProhibitedRoleModel
