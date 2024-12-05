from typing import Annotated

from pydantic import BaseModel
from rdfproxy import ConfigDict
from rdfproxy.utils._types import SPARQLBinding


class Work(BaseModel):
    model_config = ConfigDict(group_by="name")

    name: Annotated[str, SPARQLBinding("work_name")]
    viafs: Annotated[list[str], SPARQLBinding("viaf")]


class Author(BaseModel):
    model_config = ConfigDict(group_by="surname")

    gnd: str
    surname: Annotated[str, SPARQLBinding("nameLabel")]
    works: list[Work]
    education: Annotated[list[str], SPARQLBinding("educated_atLabel")]
