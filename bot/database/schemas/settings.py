from pydantic import BaseModel


class TimeOfDaySchema(BaseModel):
    time_for_night: int | None = None
    time_for_day: int | None = None


class FogOfWarSchema(BaseModel):
    show_dead_roles_after_night: bool
    show_dead_roles_after_hanging: bool
    show_roles_died_due_to_inactivity: bool
    show_killers: bool
    show_information_in_shared_chat: bool
    show_information_about_guests_at_night: bool
    show_usernames_during_voting: bool
