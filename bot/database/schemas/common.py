from pydantic import BaseModel


class IdSchema(BaseModel):
    id: int
