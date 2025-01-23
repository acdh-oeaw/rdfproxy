"""SPARQLModelAdapter class for SPARQL query result set to Pydantic model conversions."""

from collections.abc import Iterator
import logging
import math
from typing import Generic

from rdfproxy.constructor import QueryConstructor
from rdfproxy.mapper import _ModelBindingsMapper
from rdfproxy.sparql_strategies import HttpxStrategy, SPARQLStrategy
from rdfproxy.utils._types import _TModelInstance
from rdfproxy.utils.checkers.query_checker import check_query
from rdfproxy.utils.models import Page, QueryParameters


logger = logging.getLogger(__name__)


class SPARQLModelAdapter(Generic[_TModelInstance]):
    """Adapter/Mapper for SPARQL query result set to Pydantic model conversions.

    The rdfproxy.SPARQLModelAdapter class allows to run a query against an endpoint
    and map a flat SPARQL query result set to a potentially nested Pydantic model.

    SPARQLModelAdapter.query returns a Page model object with a default pagination size of 100 results.

    SPARQL bindings are implicitly assigned to model fields of the same name,
    explicit SPARQL binding to model field allocation is available with rdfproxy.SPARQLBinding.

    Result grouping is controlled through the model,
    i.e. grouping is triggered when a field of list[pydantic.BaseModel] is encountered.

    See https://github.com/acdh-oeaw/rdfproxy/tree/main/examples for examples.
    """

    def __init__(
        self,
        target: str,
        query: str,
        model: type[_TModelInstance],
        sparql_strategy: type[SPARQLStrategy] = HttpxStrategy,
    ) -> None:
        self._target = target
        self._query = check_query(query)
        self._model = model

        self.sparql_strategy = sparql_strategy(self._target)

        logger.info("Initialized SPARQLModelAdapter.")
        logger.debug("Endpoint: %s", self._target)
        logger.debug("Model: %s", self._model)
        logger.debug("Query: \n%s", self._query)

    def query(
        self, query_parameters: QueryParameters = QueryParameters()
    ) -> Page[_TModelInstance]:
        """Run a query against an endpoint and return a Page model object."""
        logger.info(
            "Running SPARQLModelAdapter.query against endpoint '%'", self._target
        )

        query_constructor = QueryConstructor(
            query=self._query,
            query_parameters=query_parameters,
            model=self._model,
        )

        count_query = query_constructor.get_count_query()
        items_query = query_constructor.get_items_query()

        logger.debug("Running items query: \n%s", items_query)

        items_query_bindings: Iterator[dict] = self.sparql_strategy.query(items_query)
        mapper = _ModelBindingsMapper(self._model, items_query_bindings)
        items: list[_TModelInstance] = mapper.get_models()

        logger.debug("Running count query: \n%s", count_query)

        count_query_bindings: Iterator[dict] = self.sparql_strategy.query(count_query)
        total: int = int(next(count_query_bindings)["cnt"])
        pages: int = math.ceil(total / query_parameters.size)

        return Page(
            items=items,
            page=query_parameters.page,
            size=query_parameters.size,
            total=total,
            pages=pages,
        )
