from database.common.base import BaseModel, IdMixin
from general import settings
from sqlalchemy import BigInteger, CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class SettingModel(IdMixin, BaseModel):
    __table_args__ = (
        CheckConstraint("time_for_night > 10"),
        CheckConstraint("time_for_day > 10"),
    )
    user_tg_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.tg_id", ondelete="CASCADE")
    )
    time_for_night: Mapped[int] = mapped_column(
        default=settings.mafia.time_for_night,
        server_default=str(settings.mafia.time_for_night),
    )
    time_for_day: Mapped[int] = mapped_column(
        default=settings.mafia.time_for_day,
        server_default=str(settings.mafia.time_for_day),
    )
    time_for_voting: Mapped[int] = mapped_column(
        default=settings.mafia.time_for_voting,
        server_default=str(settings.mafia.time_for_voting),
    )
    time_for_confirmation: Mapped[int] = mapped_column(
        default=settings.mafia.time_for_confirmation,
        server_default=str(settings.mafia.time_for_confirmation),
    )
    show_roles_after_death: Mapped[bool] = mapped_column(
        default=True, server_default="1"
    )
    show_peaceful_allies: Mapped[bool] = mapped_column(
        default=True, server_default="1"
    )
    show_killers: Mapped[bool] = mapped_column(
        default=True, server_default="1"
    )
    show_information_about_guests_at_night: Mapped[bool] = (
        mapped_column(default=True, server_default="1")
    )
    show_usernames_during_voting: Mapped[bool] = mapped_column(
        default=True, server_default="1"
    )
    show_usernames_after_confirmation: Mapped[bool] = mapped_column(
        default=False, server_default="0"
    )
    can_kill_teammates: Mapped[bool] = mapped_column(
        default=True, server_default="1"
    )
    can_marshal_kill: Mapped[bool] = mapped_column(
        default=True, server_default="1"
    )
    mafia_every_3: Mapped[bool] = mapped_column(
        default=False, server_default="0"
    )
