"""Pydantic model definitions for testing."""

from typing import Annotated

from pydantic import BaseModel
from rdfproxy.utils._types import SPARQLBinding


class SimpleModel(BaseModel):
    x: int
    y: int = 3


class NestedModel(BaseModel):
    a: str
    b: SimpleModel


class ComplexModel(BaseModel):
    p: str
    q: NestedModel


class Work(BaseModel):
    name: Annotated[str, SPARQLBinding("title")]


class Person(BaseModel):
    name: str
    work: Work
