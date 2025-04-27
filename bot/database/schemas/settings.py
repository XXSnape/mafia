from pydantic import BaseModel


class TimeOfDaySchema(BaseModel):
    time_for_night: int | None = None
    time_for_day: int | None = None


class FogOfWarSchema(BaseModel):
    show_dead_roles_after_night: bool = True
    show_dead_roles_after_hanging: bool = True
    show_roles_died_due_to_inactivity: bool = True
    show_killers: bool = True
    show_information_in_shared_chat: bool = True
    show_information_about_guests_at_night: bool = True
    show_usernames_during_voting: bool = True


class DifferentSettingsSchema(FogOfWarSchema):
    can_kill_teammates: bool = True
    can_marshal_kill: bool = True
    mafia_every_3: bool = False
