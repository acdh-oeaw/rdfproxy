"""Grouping model for RDFProxy testing."""

from pydantic import BaseModel, ConfigDict, Field


class GroupingSimpleModel(BaseModel):
    x: int
    y: int


class GroupingNestedModel(BaseModel):
    a: str
    b: GroupingSimpleModel


class GroupingComplexModel(BaseModel):
    model_config = ConfigDict(group_by="x")

    x: int = Field(exclude=True)

    p: str
    q: list[GroupingNestedModel]
