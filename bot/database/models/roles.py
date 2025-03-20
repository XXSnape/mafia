from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

from database.common.base import BaseModel


class RoleModel(BaseModel):
    name: Mapped[str] = mapped_column(primary_key=True)
    key: Mapped[str]
    grouping: Mapped[str] = mapped_column(
        ForeignKey("groupings.name", ondelete="RESTRICT")
    )
