"""Models for testing None fields."""

from pydantic import BaseModel


class SimpleNoneModel(BaseModel):
    x: None


class TwoFieldNoneModel(BaseModel):
    x: int = 1
    y: None
