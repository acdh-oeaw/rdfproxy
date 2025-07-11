"""SPARQLModelAdapter class for SPARQL query result set to Pydantic model conversions."""

import logging
import math
from typing import Generic
import warnings

from rdflib import Graph
from rdfproxy.constructor import _ItemQueryConstructor, _PageQueryConstructor
from rdfproxy.mapper import _ModelBindingsMapper
from rdfproxy.sparqlwrapper import SPARQLWrapper
from rdfproxy.utils._types import _TModelInstance
from rdfproxy.utils.checkers.item_checker import check_item_model, check_key
from rdfproxy.utils.checkers.model_checker import check_model
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
        target: str | Graph,
        query: str,
        model: type[_TModelInstance],
    ) -> None:
        self._target = target
        self._query = check_query(query)
        self._model = check_model(model)

        self.sparqlwrapper = SPARQLWrapper(self._target)

        logger.info("Initialized SPARQLModelAdapter.")
        logger.debug("Target: %s", self._target)
        logger.debug("Model: %s", self._model)
        logger.debug("Query: \n%s", self._query)

    def get_item(
        self, *, xsd_type: str | None = None, lang_tag: str | None = None, **key
    ) -> _TModelInstance:
        """Run a query against a target and return a model instance."""
        logger.info(
            "Running SPARQLModelAdapter.get_item against endpoint '%s'", self._target
        )

        check_key(key=key, query=self._query, model=self._model)

        query_constructor = _ItemQueryConstructor(
            key=key,
            xsd_type=xsd_type,
            lang_tag=lang_tag,
            query=self._query,
            model=self._model,
        )
        item_query = query_constructor.get_item_query()

        logger.debug("Running item query: \n%s", item_query)

        item_query_bindings, *_ = self.sparqlwrapper.queries(item_query)
        mapper = _ModelBindingsMapper(self._model, item_query_bindings)

        item_model = check_item_model(
            models=mapper.get_models(), model_type=self._model, key=key
        )

        return item_model

    def get_page(
        self, query_parameters: QueryParameters = QueryParameters()
    ) -> Page[_TModelInstance]:
        """Run a query against a target and return a Page model object."""
        logger.info(
            "Running SPARQLModelAdapter.get_page against endpoint '%s'", self._target
        )

        query_constructor = _PageQueryConstructor(
            query=self._query,
            query_parameters=query_parameters,
            model=self._model,
        )

        count_query = query_constructor.get_count_query()
        items_query = query_constructor.get_items_query()

        logger.debug("Running items query: \n%s", items_query)
        logger.debug("Running count query: \n%s", count_query)

        items_query_bindings, count_query_bindings = self.sparqlwrapper.queries(
            items_query, count_query
        )

        mapper = _ModelBindingsMapper(self._model, items_query_bindings)
        items: list[_TModelInstance] = mapper.get_models()

        total: int = int(next(count_query_bindings)["cnt"])
        pages: int = math.ceil(total / query_parameters.size)

        return Page(
            items=items,
            page=query_parameters.page,
            size=query_parameters.size,
            total=total,
            pages=pages,
        )

    def query(
        self, query_parameters: QueryParameters = QueryParameters()
    ) -> Page[_TModelInstance]:
        warnings.warn(
            "SPARQLModelAdapter.query is deprecated. "
            "Use SPARQLModelAdapter.get_page instead.",
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return self.get_page(query_parameters=query_parameters)
