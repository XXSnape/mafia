from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from database.common.base import BaseModel


class ChatModel(BaseModel):
    chat_id: Mapped[int] = mapped_column(BigInteger)
    user_with_settings: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("users.tg_id", ondelete="SET NULL"),
        default=None,
    )
