"""Pydantic Model definitions for rdfproxy."""

from typing import Generic

from pydantic import BaseModel, Field
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
