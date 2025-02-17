"""Pydantic Model definitions for rdfproxy."""

from enum import StrEnum
from typing import Any, Generic

from pydantic import BaseModel, Field, model_validator
from pydantic.fields import FieldInfo
from rdfproxy.utils._types import _TModelInstance
from rdfproxy.utils.utils import NamespacedFieldBindingsMap


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


class QueryParameters(
    BaseModel,
    Generic[_TModelInstance],
):
    """Query parameter model for SPARQLModelAdapter.query.

    See https://fastapi.tiangolo.com/tutorial/query-param-models/
    """

    page: int = Field(default=1, gt=0)
    size: int = Field(default=100, ge=1)

    order_by: str | None = Field(default=None)
    desc: bool = Field(default=False)

    @model_validator(mode="after")
    @classmethod
    def _check_desc_order_by_dependency(cls, data: Any) -> Any:
        """Check the dependency of desc on order_by."""
        _desc_defined, _order_by_defined = data.desc, data.order_by

        if _desc_defined and not _order_by_defined:
            raise ValueError("Field 'desc' requires Field 'order_by'.")
        return data

    def __class_getitem__(cls, model: type[_TModelInstance]):
        _order_by_fields = [(k, k) for k in NamespacedFieldBindingsMap(model).keys()]

        OrderByEnum = StrEnum("OrderByEnum", _order_by_fields)
        cls.model_fields["order_by"] = FieldInfo(annotation=OrderByEnum, default=None)

        return cls
