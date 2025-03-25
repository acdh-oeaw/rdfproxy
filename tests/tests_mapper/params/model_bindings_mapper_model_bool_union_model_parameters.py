"""Parameters for testing ModelBindingsMapper with the model_bool config option for union models."""

from typing import Optional, Union

from pydantic import BaseModel
from rdfproxy.utils._types import ConfigDict
from tests.utils._types import ModelBindingsMapperParameter


class Nested1(BaseModel):
    model_config = ConfigDict(model_bool=lambda model: False)


class Nested2(BaseModel):
    model_config = ConfigDict(model_bool=lambda model: True)


class Nested3(BaseModel):
    model_config = ConfigDict(model_bool=lambda model: False)
    x: int


class Nested4(BaseModel):
    model_config = ConfigDict(model_bool=lambda model: True)
    x: int


class Nested5(BaseModel):
    x: int | None


class Nested6(BaseModel):
    model_config = ConfigDict(model_bool="x")

    x: int | None
    y: int = 2


class Nested7(BaseModel):
    model_config = ConfigDict(model_bool={"x", "y"})

    x: int | None
    y: int | None
    z: int = 3


class Model1(BaseModel):
    nested: Nested1 | None = None


class Model2(BaseModel):
    nested: Optional[Nested1] = None


class Model3(BaseModel):
    nested: Union[Nested1, None] = None


class Model4(BaseModel):
    nested: Nested2 | None = None


class Model5(BaseModel):
    nested: Optional[Nested2] = None


class Model6(BaseModel):
    nested: Union[Nested2, None] = None


class Model7(BaseModel):
    nested: Nested3 | None = None


class Model8(BaseModel):
    nested: Optional[Nested3] = None


class Model9(BaseModel):
    nested: Union[Nested3, None] = None


class Model10(BaseModel):
    nested: Nested4 | None = None


class Model11(BaseModel):
    nested: Optional[Nested4] = None


class Model12(BaseModel):
    nested: Union[Nested4, None] = None


class Model13(BaseModel):
    nested: Nested5 | None = None


class Model14(BaseModel):
    nested: Nested5 | str = "default"


class Model15(BaseModel):
    nested: Nested6 | str = "default"


class Model16(BaseModel):
    nested: Nested7 | str = "default"


ungrouped_model_bool_union_model_parameters = [
    ModelBindingsMapperParameter(
        model=Model1,
        bindings=[{}, {}, {}],
        expected=[{"nested": None}, {"nested": None}, {"nested": None}],
    ),
    ModelBindingsMapperParameter(
        model=Model2,
        bindings=[{}, {}, {}],
        expected=[{"nested": None}, {"nested": None}, {"nested": None}],
    ),
    ModelBindingsMapperParameter(
        model=Model3,
        bindings=[{}, {}, {}],
        expected=[{"nested": None}, {"nested": None}, {"nested": None}],
    ),
    ModelBindingsMapperParameter(
        model=Model4,
        bindings=[{}, {}, {}],
        expected=[{"nested": {}}, {"nested": {}}, {"nested": {}}],
    ),
    ModelBindingsMapperParameter(
        model=Model5,
        bindings=[{}, {}, {}],
        expected=[{"nested": {}}, {"nested": {}}, {"nested": {}}],
    ),
    ModelBindingsMapperParameter(
        model=Model6,
        bindings=[{}, {}, {}],
        expected=[{"nested": {}}, {"nested": {}}, {"nested": {}}],
    ),
    # with bindings
    ModelBindingsMapperParameter(
        model=Model7,
        bindings=[{"x": 1}, {"x": 2}, {"x": 3}],
        expected=[{"nested": None}, {"nested": None}, {"nested": None}],
    ),
    ModelBindingsMapperParameter(
        model=Model8,
        bindings=[{"x": 1}, {"x": 2}, {"x": 3}],
        expected=[{"nested": None}, {"nested": None}, {"nested": None}],
    ),
    ModelBindingsMapperParameter(
        model=Model9,
        bindings=[{"x": 1}, {"x": 2}, {"x": 3}],
        expected=[{"nested": None}, {"nested": None}, {"nested": None}],
    ),
    ModelBindingsMapperParameter(
        model=Model10,
        bindings=[{"x": 1}, {"x": 2}, {"x": 3}],
        expected=[{"nested": {"x": 1}}, {"nested": {"x": 2}}, {"nested": {"x": 3}}],
    ),
    ModelBindingsMapperParameter(
        model=Model11,
        bindings=[{"x": 1}, {"x": 2}, {"x": 3}],
        expected=[{"nested": {"x": 1}}, {"nested": {"x": 2}}, {"nested": {"x": 3}}],
    ),
    ModelBindingsMapperParameter(
        model=Model12,
        bindings=[{"x": 1}, {"x": 2}, {"x": 3}],
        expected=[{"nested": {"x": 1}}, {"nested": {"x": 2}}, {"nested": {"x": 3}}],
    ),
    # with mixed bindings
    ModelBindingsMapperParameter(
        model=Model13,
        bindings=[{"x": 1}, {"x": 2}, {"x": None}],
        expected=[{"nested": {"x": 1}}, {"nested": {"x": 2}}, {"nested": None}],
    ),
    ModelBindingsMapperParameter(
        model=Model14,
        bindings=[{"x": 1}, {"x": 2}, {"x": None}],
        expected=[{"nested": {"x": 1}}, {"nested": {"x": 2}}, {"nested": "default"}],
    ),
    ModelBindingsMapperParameter(
        model=Model15,
        bindings=[{"x": 1}, {"x": 2}, {"x": None}],
        expected=[
            {"nested": {"x": 1, "y": 2}},
            {"nested": {"x": 2, "y": 2}},
            {"nested": "default"},
        ],
    ),
    ModelBindingsMapperParameter(
        model=Model16,
        bindings=[{"x": 1, "y": 2}, {"x": 2, "y": None}, {"x": None, "y": 2}],
        expected=[
            {"nested": {"x": 1, "y": 2, "z": 3}},
            {"nested": "default"},
            {"nested": "default"},
        ],
    ),
]

grouped_model_bool_union_model_parameters = []
