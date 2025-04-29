from pydantic import BaseModel

from general import settings


class TimeOfDaySchema(BaseModel):
    time_for_night: int = settings.mafia.time_for_night
    time_for_day: int = settings.mafia.time_for_day
    time_for_voting: int = settings.mafia.time_for_voting
    time_for_confirmation: int = settings.mafia.time_for_confirmation


class FogOfWarSchema(BaseModel):
    show_roles_after_death: bool = True
    show_killers: bool = True
    show_information_about_guests_at_night: bool = True
    show_usernames_during_voting: bool = True
    show_usernames_after_confirmation: bool = False


class DifferentSettingsSchema(FogOfWarSchema, TimeOfDaySchema):
    can_kill_teammates: bool = True
    can_marshal_kill: bool = True
    mafia_every_3: bool = False
