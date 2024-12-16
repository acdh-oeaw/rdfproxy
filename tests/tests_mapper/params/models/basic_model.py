"""Basic model for RDFProxy testing."""

from pydantic import BaseModel


class BasicSimpleModel(BaseModel):
    x: int
    y: int


class BasicNestedModel(BaseModel):
    a: str
    b: BasicSimpleModel


class BasicComplexModel(BaseModel):
    p: str
    q: BasicNestedModel
