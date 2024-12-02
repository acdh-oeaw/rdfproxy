"""Toy Author/Work model for testing."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict
from rdfproxy.utils._types import SPARQLBinding


class Title(BaseModel):
    name: Annotated[str, SPARQLBinding("work")]


class Work(BaseModel):
    model_config = ConfigDict(group_by="year")

    year: int
    titles: list[Title]


class Author(BaseModel):
    model_config = ConfigDict(group_by="name")

    name: Annotated[str, SPARQLBinding("author")]
    works: list[Work]
