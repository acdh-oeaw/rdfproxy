"""Basic unit tests for FieldBindingsMap"""

from typing import Annotated

from pydantic import BaseModel
from rdfproxy.utils._types import SPARQLBinding
from rdfproxy.utils.utils import FieldsBindingsMap


class Point(BaseModel):
    x: int
    y: Annotated[int, SPARQLBinding("Y_ALIAS")]
    z: Annotated[list[int], SPARQLBinding("Z_ALIAS")]


def test_basic_fields_bindings_map():
    mapping = FieldsBindingsMap(model=Point)

    assert mapping["x"] == "x"
    assert mapping["y"] == "Y_ALIAS"
    assert mapping["z"] == "Z_ALIAS"

    assert mapping.reverse["x"] == "x"
    assert mapping.reverse["Y_ALIAS"] == "y"
    assert mapping.reverse["Z_ALIAS"] == "z"
