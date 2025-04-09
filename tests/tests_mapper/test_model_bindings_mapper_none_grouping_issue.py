"""Pytest entry point for _ModelBindingsMapper tests for grouping by None-valued fields.

The tests defined here implement the cases mentioned in issue #262.
More isolated/abstract test cases are implemented in test_model_bindings_mapper_none_grouping.py
"""

from typing import Annotated

from pydantic import BaseModel
import pytest
from rdfproxy import ConfigDict, SPARQLBinding
from rdfproxy.mapper import _ModelBindingsMapper
from tests.utils._types import ModelBindingsMapperParameter


bindings_all_none = [
    {
        "subject": None,
        "event_id": None,
        "event_label": None,
    }
]

bindings_subject_uri = [
    {
        "subject": "https://hanslick.acdh.oeaw.ac.at/hsl_person_id_110",
        "event_id": None,
        "event_label": None,
    }
]


class DeeplyNested(BaseModel):
    pass


class Nested(BaseModel):
    model_config = ConfigDict(group_by="id")

    id: Annotated[str | None, SPARQLBinding("event_id")]
    label: Annotated[str | None, SPARQLBinding("event_label")]
    deeply_nested: list[DeeplyNested]


class Model(BaseModel):
    model_config = ConfigDict(group_by="id")

    id: Annotated[str | None, SPARQLBinding("subject")]
    events: list[Nested]


params = [
    ModelBindingsMapperParameter(
        model=Model, bindings=bindings_all_none, expected=[{"id": None, "events": []}]
    ),
    ModelBindingsMapperParameter(
        model=Model,
        bindings=bindings_subject_uri,
        expected=[
            {"id": "https://hanslick.acdh.oeaw.ac.at/hsl_person_id_110", "events": []}
        ],
    ),
]


@pytest.mark.parametrize(["model", "bindings", "expected"], params)
def test_model_bindings_mapper_none_grouping_issue(model, bindings, expected):
    mapper = _ModelBindingsMapper(model=model, bindings=bindings)
    models = mapper.get_models()
    assert [model.model_dump() for model in models] == expected
