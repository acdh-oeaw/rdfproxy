"""Models for testing optional fields."""

import datetime

from pydantic import BaseModel, ConfigDict


class OptionalIntFieldModel(BaseModel):
    x: int | None


class OptionalStrFieldCoerceModel(BaseModel):
    model_config = ConfigDict(coerce_numbers_to_str=True)
    x: str | None


class OptionalStrFieldModel(BaseModel):
    x: str | None


class OptionalStrFieldStrictModel(BaseModel):
    model_config = ConfigDict(strict=True)

    x: str | None


class OptionalDateFieldModel(BaseModel):
    x: datetime.date | None
