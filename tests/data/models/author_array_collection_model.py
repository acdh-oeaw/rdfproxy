from typing import Annotated

from pydantic import BaseModel
from rdfproxy.utils._types import SPARQLBinding


class Work(BaseModel):
    class Config:
        group_by = "work_name"

    name: Annotated[str, SPARQLBinding("work_name")]
    viafs: Annotated[list[str], SPARQLBinding("viaf")]


class Author(BaseModel):
    class Config:
        group_by = "nameLabel"

    gnd: str
    surname: Annotated[str, SPARQLBinding("nameLabel")]
    works: list[Work]
    education: Annotated[list[str], SPARQLBinding("educated_atLabel")]
