from general.resources import Resources
from pydantic import BaseModel


class AssetsSchema(BaseModel):
    name: Resources


class NumberOfAssetsSchema(BaseModel):
    anonymous_letters: int | None
