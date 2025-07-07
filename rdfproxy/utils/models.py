"""Pydantic Model definitions for rdfproxy."""

from enum import StrEnum
from typing import Any, Generic

from pydantic import BaseModel, Field, create_model, model_validator
from rdfproxy.utils._types import _TModelInstance
from rdfproxy.utils.utils import ModelSPARQLMap


class Page(BaseModel, Generic[_TModelInstance]):
    """Page model for rdfproxy pagination functionality.

    This model is loosely inspired by the fastapi-pagination Page class,
    see https://github.com/uriyyo/fastapi-pagination.

    Also see https://docs.pydantic.dev/latest/concepts/models/#generic-models
    for Generic Pydantic models.
    """

    items: list[_TModelInstance]
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

    def __class_getitem__(cls, model: type[_TModelInstance]):  # type: ignore
        _order_by_fields = [
            (k, k) for k in ModelSPARQLMap(model=model, recursive=True).keys()
        ]
        OrderByEnum = StrEnum("OrderByEnum", _order_by_fields)

        return create_model(
            cls.__name__, order_by=(OrderByEnum | None, None), __base__=cls
        )
