from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column


from database.common.base import BaseModel


class UserModel(BaseModel):
    tg_id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=False
    )
    balance: Mapped[int]
    registration_date: Mapped[datetime] = mapped_column(
        server_default=func.now()
    )
    is_banned: Mapped[bool] = mapped_column(default=False)
