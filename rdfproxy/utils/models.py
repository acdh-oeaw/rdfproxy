"""Pydantic Model definitions for rdfproxy."""

from typing import Any, Generic

from pydantic import BaseModel, Field, model_validator
from rdfproxy.utils._types import _TModelInstance


class Page(BaseModel, Generic[_TModelInstance]):
    """Page model for rdfproxy pagination functionality.

    This model is loosely inspired by the fastapi-pagination Page class,
    see https://github.com/uriyyo/fastapi-pagination.

    Also see https://docs.pydantic.dev/latest/concepts/models/#generic-models
    for Generic Pydantic models.
    """

    items: list[_TModelInstance] | dict[str, list[_TModelInstance]]
    page: int
    size: int
    total: int
    pages: int


class QueryParameters(BaseModel):
    """Query parameter model for SPARQLModelAdapter.query.

    See https://fastapi.tiangolo.com/tutorial/query-param-models/
    """

    page: int = Field(default=1, gt=0)
    size: int = Field(default=100, ge=1)

    order_by: str | None = Field(default=None)
    desc: bool | None = Field(default=None)

    @model_validator(mode="after")
    @classmethod
    def _check_order_by_desc_dependency(cls, data: Any) -> Any:
        """Validator for checking the semantics for ordering.

        The defaults for order_by and desc should be None.
        If only order_by is defined, desc should be set to False.
        If only desc is defined, a ValueError should be raised.
        """
        match data.order_by, data.desc:
            case None, None:
                pass
            case _, None:
                data.desc = False
            case None, _:
                raise ValueError("Field 'desc' requires field 'order_by'.")

        return data
