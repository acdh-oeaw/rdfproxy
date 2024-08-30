"""Grouping model for RDFProxy testing."""

from pydantic import BaseModel


class GroupingSimpleModel(BaseModel):
    x: int
    y: int


class GroupingNestedModel(BaseModel):
    a: str
    b: GroupingSimpleModel


class GroupingComplexModel(BaseModel):
    class Config:
        group_by = "x"

    p: str
    q: list[GroupingNestedModel]
