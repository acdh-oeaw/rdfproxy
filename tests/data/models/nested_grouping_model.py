"""Nested grouping model for RDFProxy testing."""

from pydantic import BaseModel


class NestedGroupingSimpleModel(BaseModel):
    x: int
    y: int


class NestedGroupingNestedModel(BaseModel):
    class Config:
        group_by = "y"

    a: str
    b: list[NestedGroupingSimpleModel]


class NestedGroupingComplexModel(BaseModel):
    class Config:
        group_by = "a"

    p: str
    q: list[NestedGroupingNestedModel]
