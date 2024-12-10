"""SPARQLModelAdapter class for SPARQL query result set to Pydantic model conversions."""

from collections.abc import Iterator
import math
from typing import Generic

from rdfproxy.mapper import ModelBindingsMapper
from rdfproxy.sparql_strategies import HttpxStrategy, SPARQLStrategy
from rdfproxy.utils._types import _TModelInstance
from rdfproxy.utils.models import Page, QueryParameters
from rdfproxy.utils.sparql_utils import (
    calculate_offset,
    construct_count_query,
    construct_items_query,
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
        self,
        target: str,
        query: str,
        model: type[_TModelInstance],
        sparql_strategy: type[SPARQLStrategy] = HttpxStrategy,
    ) -> None:
        self._query = query
        self._model = model

        self.sparql_strategy = sparql_strategy(target)

    def query(self, query_parameters: QueryParameters) -> Page[_TModelInstance]:
        """Run a query against an endpoint and return a Page model object."""
        count_query: str = construct_count_query(query=self._query, model=self._model)
        items_query: str = construct_items_query(
            query=self._query,
            model=self._model,
            limit=query_parameters.size,
            offset=calculate_offset(query_parameters.page, query_parameters.size),
        )

        items_query_bindings: Iterator[dict] = self.sparql_strategy.query(items_query)

        mapper = ModelBindingsMapper(self._model, *items_query_bindings)

        items: list[_TModelInstance] = mapper.get_models()
        total: int = self._get_count(count_query)
        pages: int = math.ceil(total / query_parameters.size)

        return Page(
            items=items,
            page=query_parameters.page,
            size=query_parameters.size,
            total=total,
            pages=pages,
        )

    def _get_count(self, query: str) -> int:
        """Run a count query and return the count result.

        Helper for SPARQLModelAdapter.query.
        """
        result: Iterator[dict] = self.sparql_strategy.query(query)
        return int(next(result)["cnt"])
