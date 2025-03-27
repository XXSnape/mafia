from datetime import datetime

from pydantic import BaseModel


class BeginningOfGameScheme(BaseModel):
    chat_id: int
    creator_tg_id: int
    start: datetime
