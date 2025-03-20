"""Parameters for testing ModelBindingsMapper with the model_bool config option.

The test cover all cases discussed in https://github.com/acdh-oeaw/rdfproxy/issues/110.
"""

from pydantic import BaseModel, Field, create_model
from rdfproxy import ConfigDict
from tests.utils._types import ModelBindingsMapperParameter


bindings = [
    {"parent": "x", "child": "c", "name": "foo"},
    {"parent": "y", "child": "d", "name": None},
    {"parent": "y", "child": "e", "name": None},
    {"parent": "z", "child": None, "name": None},
]


class Child1(BaseModel):
    name: str | None = None


class Child2(BaseModel):
    model_config = ConfigDict(model_bool=lambda model: True)
    name: str | None = None
    child: str | None = None


class Child3(BaseModel):
    model_config = ConfigDict(model_bool=lambda model: True)
    name: str | None = None


class Child4(BaseModel):
    model_config = ConfigDict(model_bool="child")
    name: str | None = None
    child: str | None = None


class Child5(BaseModel):
    model_config = ConfigDict(model_bool="child")
    name: str | None = None
    child: str | None = Field(default=None, exclude=True)


class Child6(BaseModel):
    model_config = ConfigDict(model_bool={"name", "child"})

    name: str | None = None
    child: str | None = None


def _create_parent_with_child(child: type[BaseModel]) -> type[BaseModel]:
    model = create_model(
        "Parent",
        parent=(str, ...),
        children=(list[child], ...),
        __config__=ConfigDict(group_by="parent"),
    )

    return model


parent_child_parameters = [
    ModelBindingsMapperParameter(
        model=_create_parent_with_child(Child1),
        bindings=bindings,
        expected=[
            {"parent": "x", "children": [{"name": "foo"}]},
            {"parent": "y", "children": []},
            {"parent": "z", "children": []},
        ],
    ),
    ModelBindingsMapperParameter(
        model=_create_parent_with_child(Child2),
        bindings=bindings,
        expected=[
            {"parent": "x", "children": [{"name": "foo", "child": "c"}]},
            {
                "parent": "y",
                "children": [
                    {"name": None, "child": "d"},
                    {"name": None, "child": "e"},
                ],
            },
            {"parent": "z", "children": [{"name": None, "child": None}]},
        ],
    ),
    ModelBindingsMapperParameter(
        model=_create_parent_with_child(Child3),
        bindings=bindings,
        expected=[
            {"parent": "x", "children": [{"name": "foo"}]},
            {"parent": "y", "children": [{"name": None}]},
            {"parent": "z", "children": [{"name": None}]},
        ],
    ),
    ModelBindingsMapperParameter(
        model=_create_parent_with_child(Child4),
        bindings=bindings,
        expected=[
            {"parent": "x", "children": [{"name": "foo", "child": "c"}]},
            {
                "parent": "y",
                "children": [
                    {"name": None, "child": "d"},
                    {"name": None, "child": "e"},
                ],
            },
            {"parent": "z", "children": []},
        ],
    ),
    ModelBindingsMapperParameter(
        model=_create_parent_with_child(Child5),
        bindings=bindings,
        expected=[
            {"parent": "x", "children": [{"name": "foo"}]},
            {"parent": "y", "children": [{"name": None}, {"name": None}]},
            {"parent": "z", "children": []},
        ],
    ),
    ModelBindingsMapperParameter(
        model=_create_parent_with_child(Child6),
        bindings=bindings,
        expected=[
            {"parent": "x", "children": [{"name": "foo", "child": "c"}]},
            {"parent": "y", "children": []},
            {"parent": "z", "children": []},
        ],
    ),
]
