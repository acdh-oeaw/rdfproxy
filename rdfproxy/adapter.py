"""SPARQLModelAdapter class for SPARQL query result set to Pydantic model conversions."""

from collections.abc import Iterator
import math
from typing import Generic

from SPARQLWrapper import JSON, SPARQLWrapper
from rdfproxy.mapper import ModelBindingsMapper
from rdfproxy.utils._types import _TModelInstance
from rdfproxy.utils.models import Page
from rdfproxy.utils.sparql_utils import (
    calculate_offset,
    construct_count_query,
    query_with_wrapper,
    ungrouped_pagination_base_query,
)


class SPARQLModelAdapter(Generic[_TModelInstance]):
    """Adapter/Mapper for SPARQL query result set to Pydantic model conversions.

    The rdfproxy.SPARQLModelAdapter class allows to run a query against an endpoint
    and map a flat SPARQL query result set to a potentially nested Pydantic model.

    SPARQLModelAdapter.query returns a Page model object with a default pagination size of 100 results.

    SPARQL bindings are implicitly assigned to model fields of the same name,
    explicit SPARQL binding to model field allocation is available with typing.Annotated and rdfproxy.SPARQLBinding.

    Result grouping is controlled through the model,
    i.e. grouping is triggered when a field of list[pydantic.BaseModel] is encountered.
    """

    def __init__(
        self, target: str | SPARQLWrapper, query: str, model: type[_TModelInstance]
    ) -> None:
        self._query = query
        self._model = model

        self.sparql_wrapper: SPARQLWrapper = (
            SPARQLWrapper(target) if isinstance(target, str) else target
        )
        self.sparql_wrapper.setReturnFormat(JSON)

    def query(
        self,
        *,
        page: int = 1,
        size: int = 100,
    ) -> Page[_TModelInstance]:
        """Run a query against an endpoint and return a Page model object."""
        count_query: str = construct_count_query(query=self._query, model=self._model)
        items_query: str = ungrouped_pagination_base_query.substitute(
            query=self._query, offset=calculate_offset(page, size), limit=size
        )

        items_query_bindings: Iterator[dict] = query_with_wrapper(
            query=items_query, sparql_wrapper=self.sparql_wrapper
        )

        mapper = ModelBindingsMapper(self._model, *items_query_bindings)

        items: list[_TModelInstance] = mapper.get_models()
        total: int = self._get_count(count_query)
        pages: int = math.ceil(total / size)

        return Page(items=items, page=page, size=size, total=total, pages=pages)

    def _get_count(self, query: str) -> int:
        """Run a count query and return the count result.

        Helper for SPARQLModelAdapter.query.
        """
        result: Iterator[dict] = query_with_wrapper(
            query=query, sparql_wrapper=self.sparql_wrapper
        )
        return int(next(result)["cnt"])
