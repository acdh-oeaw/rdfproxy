"""Tests for strict=True/False model instantiation with rdfproxy.SPARQLWrapper Python-casting."""

from pydantic import BaseModel, ConfigDict, ValidationError
import pytest


query_str_decimal = """
select *
where {
  values (?x) {
     ('2.2')
    }
}
"""

query_decimal = """
select *
where {
  values (?x) {
     (1.0)
    }
}
"""


class StrFloatModel(BaseModel):
    """Will coerce to float when given a str."""

    x: float


class StrFloatModelStrict(BaseModel):
    """Will fail when given a str."""

    model_config = ConfigDict(strict=True)
    x: float


class IntModel(BaseModel):
    """Will coerce when given a decimal.Decimal."""

    x: int


class IntModelStrict(BaseModel):
    """Will fail when given a decimal.Decimal."""

    model_config = ConfigDict(strict=True)
    x: int


@pytest.mark.parametrize(
    ["query", "model"],
    [(query_str_decimal, StrFloatModel), (query_decimal, IntModel)],
)
def test_sparql_wrapper_model_instantiate_success(sparql_wrapper, query, model):
    """Check if model instantiation with wrong type SUCCEEDS with type coercion."""
    (result, *_), *_ = sparql_wrapper.queries(query)

    assert model(**dict(result))


@pytest.mark.parametrize(
    ["query", "model"],
    [(query_str_decimal, StrFloatModelStrict), (query_decimal, IntModelStrict)],
)
def test_sparql_wrapper_model_instantiate_fail(sparql_wrapper, query, model):
    """Check if model instantiation with wrong type FAILS with strict model."""
    (result, *_), *_ = sparql_wrapper.queries(query)

    with pytest.raises(ValidationError):
        assert model(**dict(result))
