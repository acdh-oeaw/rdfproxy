"""Pydantic model definitions for testing."""

from pydantic import BaseModel


class SimpleModel(BaseModel):
    x: int
    y: int = 3


class NestedModel(BaseModel):
    a: str
    b: SimpleModel


class ComplexModel(BaseModel):
    p: str
    q: NestedModel
