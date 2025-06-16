from database.common.base import BaseModel
from general.resources import Resources
from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column


class AssetModel(BaseModel):
    __table_args__ = (CheckConstraint("cost > 0"),)
    name: Mapped[Resources] = mapped_column(primary_key=True)
    cost: Mapped[int]
