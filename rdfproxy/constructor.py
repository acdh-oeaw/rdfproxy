from typing import Any

from rdflib import Literal
from rdfproxy.utils._types import _TModelInstance
from rdfproxy.utils.models import QueryParameters
from rdfproxy.utils.sparql_utils import (
    add_solution_modifier,
    get_query_projection,
    inject_into_query,
    remove_sparql_prefixes,
    replace_query_select_clause,
)
from rdfproxy.utils.utils import (
    FieldsBindingsMap,
    OrderableFieldsBindingsMap,
    QueryConstructorComponent as component,
    compose_left,
)


class _ItemQueryConstructor:
    """SPARQL query constructor for SPARQLModelAdapter.get_item.

    The class encapsulates dynamic SPARQL query modification logic
    for single item requests according to an ID key.
    """

    def __init__(
        self,
        key: dict[str, Any],
        xsd_type: str | None,
        lang_tag: str | None,
        query: str,
        model: type[_TModelInstance],
    ) -> None:
        self.key = key
        self.xsd_type = xsd_type
        self.lang_tag = lang_tag
        self.query = query

        self.bindings_map = FieldsBindingsMap(model)

    def get_item_query(self) -> str:
        """Construct a SPARQL item query for use in rdfproxy.SPARQLModelAdapter."""
        detail_filter_clause: str = self._get_item_filter_clause()
        return inject_into_query(
            self.query, detail_filter_clause, inject_into_pattern=False
        )

    def _get_item_filter_clause(self) -> str:
        """Compute a FILTER clause for SPARQL item query construction."""

        (_key_key, _key_value), *_ = self.key.items()

        key_key = self.bindings_map[_key_key]
        key_value = Literal(
            _key_value
        )._quote_encode()  # Literal.n3 would also be an option

        match (self.xsd_type, self.lang_tag):
            case None, None:
                filter_clause = f"filter (str(?{key_key}) = {key_value})"
            case xsd_type, None:
                filter_clause = f"filter (?{key_key} = {key_value}^^<{xsd_type}>)"
            case None, lang_tag:
                filter_clause = f"filter (?{key_key} = {key_value}@{lang_tag})"
            case xsd_type, lang_tag:
                raise ValueError(
                    "Parameters xsd_type and lang_tag are mutually exclusive."
                )
            case _:  # pragma: no cover
                assert False, "This should never happen."

        return filter_clause


class _PageQueryConstructor:
    """SPARQL query constructor SPARQLModelAdapter.get_page.

    The class encapsulates dynamic SPARQL query modification logic
    for implementing purely SPARQL-based, deterministic pagination.

    Public methods get_items_query and get_count_query are used in rdfproxy.SPARQLModelAdapter
    to construct queries for retrieving arguments for Page object instantiation.
    """

    def __init__(
        self,
        query: str,
        query_parameters: QueryParameters,
        model: type[_TModelInstance],
    ) -> None:
        self.query = query
        self.query_parameters = query_parameters
        self.model = model

        self.bindings_map = FieldsBindingsMap(model)
        self.orderable_bindings_map = OrderableFieldsBindingsMap(model)

        self.group_by: str | None = self.bindings_map.get(
            model.model_config.get("group_by")
        )
        self.order_by: str | None = (
            None
            if self.query_parameters.order_by is None
            else self.orderable_bindings_map[self.query_parameters.order_by]
        )

    def get_items_query(self) -> str:
        """Construct a SPARQL items query for use in rdfproxy.SPARQLModelAdapter."""
        if self.group_by is None:
            return self._get_ungrouped_items_query()
        return self._get_grouped_items_query()

    def get_count_query(self) -> str:
        """Construct a SPARQL count query for use in rdfproxy.SPARQLModelAdapter"""
        if self.group_by is None:
            select_clause = "select (count(*) as ?cnt)"
        else:
            select_clause = f"select (count(distinct ?{self.group_by}) as ?cnt)"

        return replace_query_select_clause(self.query, select_clause)

    @staticmethod
    def _calculate_offset(page: int, size: int) -> int:
        """Calculate the offset value for paginated SPARQL templates."""
        match page:
            case 1:
                return 0
            case 2:
                return size
            case _:
                return size * (page - 1)

    def _get_grouped_items_query(self) -> str:
        """Construct a SPARQL items query for grouped models."""
        filter_clause: str | None = self._compute_filter_clause()
        select_clause: str = self._compute_select_clause()
        order_by_value: str = self._compute_order_by_value()
        limit, offset = self._compute_limit_offset()

        subquery = compose_left(
            remove_sparql_prefixes,
            component(replace_query_select_clause, repl=select_clause),
            component(inject_into_query, injectant=filter_clause),
            component(
                add_solution_modifier,
                order_by=order_by_value,
                limit=limit,
                offset=offset,
            ),
        )(self.query)

        return add_solution_modifier(
            inject_into_query(self.query, subquery), order_by=order_by_value
        )

    def _get_ungrouped_items_query(self) -> str:
        """Construct a SPARQL items query for ungrouped models."""
        filter_clause: str | None = self._compute_filter_clause()
        order_by_value: str = self._compute_order_by_value()
        limit, offset = self._compute_limit_offset()

        return compose_left(
            component(inject_into_query, injectant=filter_clause),
            component(
                add_solution_modifier,
                order_by=order_by_value,
                limit=limit,
                offset=offset,
            ),
        )(self.query)

    def _compute_limit_offset(self) -> tuple[int, int]:
        """Calculate limit and offset values for SPARQL-based pagination."""
        limit = self.query_parameters.size
        offset = self._calculate_offset(
            self.query_parameters.page, self.query_parameters.size
        )

        return limit, offset

    def _compute_filter_clause(self) -> str | None:
        """Stub: Always None for now."""
        return None

    def _compute_select_clause(self):
        """Stub: Static SELECT clause for now."""
        return f"select distinct ?{self.group_by}"

    def _compute_order_by_value(self):
        """Compute a value for ORDER BY used in RDFProxy query modification."""
        match self.group_by, self.order_by:
            case None, None:
                return f"?{get_query_projection(self.query)[0]}"
            case group_by, None:
                return f"?{group_by}"

            case _, order_by:
                return f"{'DESC' if self.query_parameters.desc else 'ASC'}(?{order_by})"

            case _:  # pragma: no cover
                assert False, "Unreachable case in _compute_order_by_value"
