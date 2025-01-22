"""Nested grouping model for RDFProxy testing."""

from pydantic import BaseModel, Field
from rdfproxy import ConfigDict


class NestedGroupingSimpleModel(BaseModel):
    x: int
    y: int


class NestedGroupingNestedModel(BaseModel):
    model_config = ConfigDict(group_by="y")

    y: int = Field(exclude=True)

    a: str
    b: list[NestedGroupingSimpleModel]


class NestedGroupingComplexModel(BaseModel):
    model_config = ConfigDict(group_by="a")

    a: str = Field(exclude=True)

    p: str
    q: list[NestedGroupingNestedModel]


class NestedComplexModel(BaseModel):
    model_config = ConfigDict(group_by="a")

    a: str = Field(exclude=True)
    b: NestedGroupingSimpleModel


class GroupingNestedComplexModel(BaseModel):
    model_config = ConfigDict(group_by="a")

    a: str = Field(exclude=True)
    b: NestedGroupingSimpleModel
    c: list[NestedGroupingSimpleModel]
