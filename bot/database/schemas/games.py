from datetime import datetime

from pydantic import BaseModel


class BeginningOfGameSchema(BaseModel):
    group_id: int
    start: datetime


class EndOfGameSchema(BaseModel):
    id: int
    winning_group: str
    number_of_nights: int
    end: datetime
