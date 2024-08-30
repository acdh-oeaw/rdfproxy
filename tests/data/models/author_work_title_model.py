"""Toy Author/Work model for testing."""

from typing import Annotated

from pydantic import BaseModel
from rdfproxy.utils._types import SPARQLBinding


class Title(BaseModel):
    name: Annotated[str, SPARQLBinding("work")]


class Work(BaseModel):
    class Config:
        group_by = "year"

    year: int
    titles: list[Title]


class Author(BaseModel):
    class Config:
        group_by = "author"

    name: Annotated[str, SPARQLBinding("author")]
    works: list[Work]
