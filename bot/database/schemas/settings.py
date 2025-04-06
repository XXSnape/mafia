from pydantic import BaseModel


class TimeOfDaySchema(BaseModel):
    time_for_night: int | None = None
    time_for_day: int | None = None
