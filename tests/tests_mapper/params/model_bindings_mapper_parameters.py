import datetime

from tests.tests_mapper.params.models.author_array_collection_model import (
    Author as ArrayAuthor,
)
from tests.tests_mapper.params.models.author_work_title_model import Author
from tests.tests_mapper.params.models.basic_model import (
    BasicComplexModel,
    BasicNestedModel,
    BasicSimpleModel,
)
from tests.tests_mapper.params.models.empty_default_only_model import DefaultOnly, Empty
from tests.tests_mapper.params.models.grouping_model import GroupingComplexModel
from tests.tests_mapper.params.models.model_validator_model import PointNotOrigin
from tests.tests_mapper.params.models.nested_grouping_model import (
    GroupingNestedComplexModel,
    NestedComplexModel,
    NestedGroupingComplexModel,
)
from tests.tests_mapper.params.models.none_models import (
    SimpleNoneModel,
    TwoFieldNoneModel,
)
from tests.tests_mapper.params.models.optional_fields_models import (
    OptionalDateFieldModel,
    OptionalIntFieldModel,
    OptionalStrFieldCoerceModel,
    OptionalStrFieldModel,
    OptionalStrFieldStrictModel,
)
from tests.utils._types import ModelBindingsMapperParameter


model_validator_parameters = [
    ModelBindingsMapperParameter(
        model=PointNotOrigin,
        bindings=[{"x": 1, "y": 2}],
        expected=[{"x": 1, "y": 2}],
    )
]

author_array_collection_parameters = [
    ModelBindingsMapperParameter(
        model=ArrayAuthor,
        bindings=[
            {
                "work": "http://www.wikidata.org/entity/Q1497409",
                "gnd": "119359464",
                "work_name": "Geb\u00fcrtig",
                "nameLabel": "Schindel",
            },
            {
                "work": "http://www.wikidata.org/entity/Q15805238",
                "gnd": "115612815",
                "work_name": "Der alte K\u00f6nig in seinem Exil",
                "nameLabel": "Geiger",
                "viaf": "299260555",
                "educated_atLabel": "University of Vienna",
            },
            {
                "work": "http://www.wikidata.org/entity/Q15805238",
                "gnd": "115612815",
                "work_name": "Der alte K\u00f6nig in seinem Exil",
                "nameLabel": "Geiger",
                "viaf": "6762154387354230970008",
                "educated_atLabel": "University of Vienna",
            },
            {
                "work": "http://www.wikidata.org/entity/Q58038819",
                "gnd": "115612815",
                "work_name": "Unter der Drachenwand",
                "nameLabel": "Geiger",
                "viaf": "2277151717053313900002",
                "educated_atLabel": "University of Vienna",
            },
            {
                "work": "http://www.wikidata.org/entity/Q100266054",
                "gnd": "1136992030",
                "work_name": "Das fl\u00fcssige Land",
                "nameLabel": "Edelbauer",
                "educated_atLabel": "University of Vienna",
            },
            {
                "work": "http://www.wikidata.org/entity/Q100266054",
                "gnd": "1136992030",
                "work_name": "Das fl\u00fcssige Land",
                "nameLabel": "Edelbauer",
                "educated_atLabel": "University of Applied Arts Vienna",
            },
        ],
        expected=[
            {
                "gnd": "119359464",
                "surname": "Schindel",
                "works": [{"name": "Geb\u00fcrtig", "viafs": []}],
                "education": [],
            },
            {
                "gnd": "115612815",
                "surname": "Geiger",
                "works": [
                    {
                        "name": "Der alte K\u00f6nig in seinem Exil",
                        "viafs": ["299260555", "6762154387354230970008"],
                    },
                    {
                        "name": "Unter der Drachenwand",
                        "viafs": ["2277151717053313900002"],
                    },
                ],
                "education": ["University of Vienna"],
            },
            {
                "gnd": "1136992030",
                "surname": "Edelbauer",
                "works": [{"name": "Das fl\u00fcssige Land", "viafs": []}],
                "education": [
                    "University of Vienna",
                    "University of Applied Arts Vienna",
                ],
            },
        ],
    )
]


author_work_title_parameters = [
    ModelBindingsMapperParameter(
        model=Author,
        bindings=[
            {"author": "Author 1", "work": "Work 1", "year": 2000},
            {"author": "Author 2", "work": "Work 4", "year": 2000},
            {"author": "Author 1", "work": "Work 2", "year": 2000},
            {"author": "Author 1", "work": "Work 3", "year": 2001},
        ],
        expected=[
            {
                "name": "Author 1",
                "works": [
                    {"year": 2000, "titles": [{"name": "Work 1"}, {"name": "Work 2"}]},
                    {"year": 2001, "titles": [{"name": "Work 3"}]},
                ],
            },
            {
                "name": "Author 2",
                "works": [{"year": 2000, "titles": [{"name": "Work 4"}]}],
            },
        ],
    )
]


basic_parameters = [
    ModelBindingsMapperParameter(
        model=BasicSimpleModel, bindings=[{"x": 1, "y": 2}], expected=[{"x": 1, "y": 2}]
    ),
    ModelBindingsMapperParameter(
        model=BasicSimpleModel,
        bindings=[{"x": 3, "y": 4}, {"x": 5, "y": 6}],
        expected=[{"x": 3, "y": 4}, {"x": 5, "y": 6}],
    ),
    ModelBindingsMapperParameter(
        model=BasicNestedModel,
        bindings=[{"a": "a value", "x": 1, "y": 2}],
        expected=[{"a": "a value", "b": {"x": 1, "y": 2}}],
    ),
    ModelBindingsMapperParameter(
        model=BasicNestedModel,
        bindings=[{"a": "a value", "x": 1, "y": 2}, {"a": "a value", "x": 3, "y": 4}],
        expected=[
            {"a": "a value", "b": {"x": 1, "y": 2}},
            {"a": "a value", "b": {"x": 3, "y": 4}},
        ],
    ),
    # test for empty string/falsy fields
    ModelBindingsMapperParameter(
        model=BasicNestedModel,
        bindings=[
            {"a": "a value", "x": 1, "y": 2},
            {"a": "a value", "x": 3, "y": 4},
            {"a": "", "x": 3, "y": 4},
        ],
        expected=[
            {"a": "a value", "b": {"x": 1, "y": 2}},
            {"a": "a value", "b": {"x": 3, "y": 4}},
            {"a": "", "b": {"x": 3, "y": 4}},
        ],
    ),
    ModelBindingsMapperParameter(
        model=BasicComplexModel,
        bindings=[{"a": "a value", "x": 1, "y": 2, "p": "p value"}],
        expected=[{"p": "p value", "q": {"a": "a value", "b": {"x": 1, "y": 2}}}],
    ),
    ModelBindingsMapperParameter(
        model=BasicComplexModel,
        bindings=[
            {"a": "a value", "x": 1, "y": 2, "p": "p value"},
            {"a": "a value", "x": 3, "y": 4, "p": "p value"},
        ],
        expected=[
            {"p": "p value", "q": {"a": "a value", "b": {"x": 1, "y": 2}}},
            {"p": "p value", "q": {"a": "a value", "b": {"x": 3, "y": 4}}},
        ],
    ),
    # tests for empty string/falsy fields
    ModelBindingsMapperParameter(
        model=BasicComplexModel,
        bindings=[{"a": "", "x": 1, "y": 2, "p": "p value"}],
        expected=[{"p": "p value", "q": {"a": "", "b": {"x": 1, "y": 2}}}],
    ),
    ModelBindingsMapperParameter(
        model=BasicComplexModel,
        bindings=[{"a": "a value", "x": 1, "y": 2, "p": ""}],
        expected=[{"p": "", "q": {"a": "a value", "b": {"x": 1, "y": 2}}}],
    ),
]


grouping_parameters = [
    ModelBindingsMapperParameter(
        model=GroupingComplexModel,
        bindings=[{"a": "a value", "x": 1, "y": 2, "p": "p value"}],
        expected=[{"p": "p value", "q": [{"a": "a value", "b": {"x": 1, "y": 2}}]}],
    ),
    ModelBindingsMapperParameter(
        model=GroupingComplexModel,
        bindings=[
            {"a": "a value", "x": 1, "y": 2, "p": "p value"},
            {"a": "a value", "x": 3, "y": 4, "p": "p value"},
        ],
        expected=[
            {"p": "p value", "q": [{"a": "a value", "b": {"x": 1, "y": 2}}]},
            {"p": "p value", "q": [{"a": "a value", "b": {"x": 3, "y": 4}}]},
        ],
    ),
    ModelBindingsMapperParameter(
        model=GroupingComplexModel,
        bindings=[
            {"a": "a value", "x": 1, "y": 2, "p": "p value"},
            {"a": "a value", "x": 3, "y": 4, "p": "p value"},
            {"a": "a value", "x": 1, "y": 4, "p": "p value"},
        ],
        expected=[
            {
                "p": "p value",
                "q": [
                    {"a": "a value", "b": {"x": 1, "y": 2}},
                    {"a": "a value", "b": {"x": 1, "y": 4}},
                ],
            },
            {"p": "p value", "q": [{"a": "a value", "b": {"x": 3, "y": 4}}]},
        ],
    ),
]


grouping_nested_model_parameters = [
    ModelBindingsMapperParameter(
        model=NestedComplexModel,
        bindings=[
            {"x": 1, "y": 2, "a": "a value 1", "p": "p value 1"},
            {"x": 1, "y": 2, "a": "a value 2", "p": "p value 2"},
            {"x": 1, "y": 3, "a": "a value 3", "p": "p value 3"},
            {"x": 2, "y": 2, "a": "a value 1", "p": "p value 4"},
        ],
        expected=[
            {"b": {"x": 1, "y": 2}},
            {"b": {"x": 1, "y": 2}},
            {"b": {"x": 1, "y": 3}},
        ],
    ),
    ModelBindingsMapperParameter(
        model=GroupingNestedComplexModel,
        bindings=[
            {"x": 1, "y": 2, "a": "a value 1", "p": "p value 1"},
            {"x": 1, "y": 2, "a": "a value 2", "p": "p value 2"},
            {"x": 1, "y": 3, "a": "a value 3", "p": "p value 3"},
            {"x": 2, "y": 2, "a": "a value 1", "p": "p value 4"},
        ],
        expected=[
            {"b": {"x": 1, "y": 2}, "c": [{"x": 1, "y": 2}, {"x": 2, "y": 2}]},
            {"b": {"x": 1, "y": 2}, "c": [{"x": 1, "y": 2}]},
            {"b": {"x": 1, "y": 3}, "c": [{"x": 1, "y": 3}]},
        ],
    ),
]

empty_default_only_model_parameters = [
    ModelBindingsMapperParameter(
        model=Empty,
        bindings=[],
        expected=[],
    ),
    ModelBindingsMapperParameter(
        model=DefaultOnly,
        bindings=[],
        expected=[],
    ),
    ## revise
    ModelBindingsMapperParameter(
        model=Empty,
        bindings=[{"whatever": 1}, {"whatever": 2}],
        expected=[{}, {}],
    ),
    ModelBindingsMapperParameter(
        model=DefaultOnly,
        bindings=[{"whatever": 1}, {"whatever": 2}],
        expected=[{"x": 1}, {"x": 1}],
    ),
]

none_model_parameters = [
    ModelBindingsMapperParameter(
        model=SimpleNoneModel,
        bindings=[{"x": None}],
        expected=[{"x": None}],
    ),
    ModelBindingsMapperParameter(
        model=TwoFieldNoneModel,
        bindings=[{"y": None}],
        expected=[{"x": 1, "y": None}],
    ),
    ModelBindingsMapperParameter(
        model=TwoFieldNoneModel,
        bindings=[{"x": 2, "y": None}],
        expected=[{"x": 2, "y": None}],
    ),
]

optional_fields_model_parameters = [
    ModelBindingsMapperParameter(
        model=OptionalIntFieldModel,
        bindings=[{"x": 1}, {"x": None}],
        expected=[{"x": 1}, {"x": None}],
    ),
    ModelBindingsMapperParameter(
        model=OptionalStrFieldCoerceModel,
        bindings=[{"x": 1}, {"x": None}],
        expected=[{"x": "1"}, {"x": None}],
    ),
    ModelBindingsMapperParameter(
        model=OptionalStrFieldModel,
        bindings=[{"x": "1"}, {"x": None}],
        expected=[{"x": "1"}, {"x": None}],
    ),
    ModelBindingsMapperParameter(
        model=OptionalStrFieldStrictModel,
        bindings=[{"x": "1"}, {"x": None}],
        expected=[{"x": "1"}, {"x": None}],
    ),
    ModelBindingsMapperParameter(
        model=OptionalDateFieldModel,
        bindings=[{"x": datetime.date.today()}, {"x": None}],
        expected=[{"x": datetime.date.today()}, {"x": None}],
    ),
]

empty_bindings_model_parameters = [
    ModelBindingsMapperParameter(
        model=model,
        bindings=[],
        expected=[],
    )
    for model in [
        BasicComplexModel,
        BasicNestedModel,
        BasicSimpleModel,
        GroupingNestedComplexModel,
        NestedComplexModel,
        NestedGroupingComplexModel,
        SimpleNoneModel,
        TwoFieldNoneModel,
        OptionalDateFieldModel,
        OptionalIntFieldModel,
        OptionalStrFieldCoerceModel,
        OptionalStrFieldModel,
        OptionalStrFieldStrictModel,
    ]
]
