"""Simple dummy models e.g. for count query constructor testing."""

from pydantic import BaseModel
from rdfproxy import ConfigDict


class Dummy(BaseModel):
    pass


class GroupedDummy(BaseModel):
    model_config = ConfigDict(group_by="x")

    x: int
