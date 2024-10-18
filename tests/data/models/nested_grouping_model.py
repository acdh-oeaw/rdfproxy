"""Nested grouping model for RDFProxy testing."""

from pydantic import BaseModel, ConfigDict


class NestedGroupingSimpleModel(BaseModel):
    x: int
    y: int


class NestedGroupingNestedModel(BaseModel):
    model_config = ConfigDict(group_by="y")

    a: str
    b: list[NestedGroupingSimpleModel]


class NestedGroupingComplexModel(BaseModel):
    model_config = ConfigDict(group_by="a")

    p: str
    q: list[NestedGroupingNestedModel]
