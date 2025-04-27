from pydantic import BaseModel


class TimeOfDaySchema(BaseModel):
    time_for_night: int | None = None
    time_for_day: int | None = None


class FogOfWarSchema(BaseModel):
    show_dead_roles_after_night: bool | None = None
    show_dead_roles_after_hanging: bool | None = None
    show_roles_died_due_to_inactivity: bool | None = None
    show_killers: bool | None = None
    show_information_in_shared_chat: bool | None = None
    show_information_about_guests_at_night: bool | None = None
    show_usernames_during_voting: bool | None = None


class DifferentSettingsSchema(FogOfWarSchema):
    can_kill_teammates: bool | None = None
    can_marshal_kill: bool | None = None
    mafia_every_3: bool | None = None
