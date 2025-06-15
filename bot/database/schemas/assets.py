from pydantic import BaseModel
from general.resources import Resources


class AssetsSchema(BaseModel):
    name: Resources
