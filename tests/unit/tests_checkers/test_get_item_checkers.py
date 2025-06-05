"""Unit tests for checkers running SPARQLModelAdapter.get_item."""

from typing import Annotated, Any, NamedTuple

from pydantic import BaseModel
import pytest
from rdfproxy.utils._types import SPARQLBinding
from rdfproxy.utils.checkers.item_checker import check_item_model, check_key
from rdfproxy.utils.exceptions import (
    MultipleResultsFound,
    NoResultsFound,
    UnprojectedKeyBindingException,
)


class Model(BaseModel):
    x: int
    y: Annotated[int, SPARQLBinding("y_alias")]


query = """
PREFIX ex: <http://www.exmaple.com/>

select ?x ?y where {?x ex:p ?y}
"""

query_alias = """
PREFIX ex: <http://www.exmaple.com/>

select ?x_alias ?y_alias where {?x ex:p ?y_alias}
"""


class KeyParameters(NamedTuple):
    key: dict[str, Any]
    query: str
    model: type[BaseModel]


valid_keys = [
    KeyParameters(key={"x": 1}, query=query, model=Model),
    KeyParameters(key={"y": 1}, query=query_alias, model=Model),
]

invalid_keys_len = [
    KeyParameters(key={}, query=query, model=Model),
    KeyParameters(key={"x": 1, "y": 2}, query=query_alias, model=Model),
]

invalid_keys_projection = [
    KeyParameters(key={"y": 1}, query=query, model=Model),
    KeyParameters(key={"x": 1}, query=query_alias, model=Model),
]

invalid_keys_key_error = [
    KeyParameters(key={"dne": 1}, query=query_alias, model=Model),
    KeyParameters(key={"y_alias": 1}, query=query_alias, model=Model),
]


@pytest.mark.parametrize("params", valid_keys)
def test_valid_keys(params):
    assert check_key(key=params.key, query=params.query, model=params.model)


@pytest.mark.parametrize("params", invalid_keys_projection)
def test_invalid_keys_projection(params):
    with pytest.raises(UnprojectedKeyBindingException):
        assert check_key(key=params.key, query=params.query, model=params.model)


@pytest.mark.parametrize("params", invalid_keys_key_error)
def test_invalid_keys_key_error(params):
    with pytest.raises(KeyError):
        assert check_key(key=params.key, query=params.query, model=params.model)


@pytest.mark.parametrize("params", invalid_keys_len)
def test_invalid_keys_len(params):
    with pytest.raises(ValueError):
        assert check_key(key=params.key, query=params.query, model=params.model)


def test_check_item_model_multi_results():
    models = [Model(x=1, y=2), Model(x=3, y=4)]

    with pytest.raises(MultipleResultsFound):
        check_item_model(models=models, model_type=Model, key={"dne": "dummy"})


def test_check_item_model_no_result():
    models = []

    with pytest.raises(NoResultsFound):
        check_item_model(models=models, model_type=Model, key={"dne": "dummy"})
