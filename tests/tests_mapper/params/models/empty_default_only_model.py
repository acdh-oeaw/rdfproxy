"""Models for testing empty/defaul-only model cases."""

from pydantic import BaseModel


class Empty(BaseModel):
    pass


class DefaultOnly(BaseModel):
    x: int = 1
