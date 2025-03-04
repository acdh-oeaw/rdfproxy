"""Unit tests for QueryParameters model."""

from typing import Any, NamedTuple

import pytest
from rdfproxy.utils.models import QueryParameters


class OrderableFieldsParameters(NamedTuple):
    query_parameters: QueryParameters
    expected: tuple[Any, Any]


order_by_params = [
    OrderableFieldsParameters(
        query_parameters=QueryParameters(), expected=(None, None)
    ),
    OrderableFieldsParameters(
        query_parameters=QueryParameters(order_by="value"), expected=("value", False)
    ),
    OrderableFieldsParameters(
        query_parameters=QueryParameters(order_by="value", desc=True),
        expected=("value", True),
    ),
]


@pytest.mark.parametrize(["query_parameters", "expected"], order_by_params)
def test_query_parameters_order_by_desc_fields(query_parameters, expected):
    assert (query_parameters.order_by, query_parameters.desc) == expected


@pytest.mark.parametrize("params", [{"desc": True}, {"desc": False}])
def test_sad_query_parameters_order_by_desc_fields(params):
    with pytest.raises(ValueError):
        QueryParameters(**params)
