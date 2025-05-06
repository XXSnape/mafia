from general import settings
from pydantic import BaseModel


class TimeOfDaySchema(BaseModel):
    time_for_night: int = settings.mafia.time_for_night
    time_for_day: int = settings.mafia.time_for_day
    time_for_voting: int = settings.mafia.time_for_voting
    time_for_confirmation: int = settings.mafia.time_for_confirmation


class DifferentSettingsSchema(TimeOfDaySchema):
    show_roles_after_death: bool = True
    show_peaceful_allies: bool = True
    show_killers: bool = True
    show_information_about_guests_at_night: bool = True
    show_usernames_during_voting: bool = True
    show_usernames_after_confirmation: bool = False
    can_kill_teammates: bool = True
    can_marshal_kill: bool = True
    mafia_every_3: bool = False
    allow_betting: bool = True
    speed_up_nights_and_voting: bool = False
