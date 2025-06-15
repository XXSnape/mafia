from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from general.assets import Assets
from database.common.base import BaseModel


class AssetModel(BaseModel):
    __table_args__ = (CheckConstraint("cost > 0"),)
    name: Mapped[Assets] = mapped_column(primary_key=True)
    cost: Mapped[int]
