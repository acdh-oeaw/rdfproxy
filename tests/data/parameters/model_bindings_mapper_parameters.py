from tests.data.models.author_array_collection_model import Author as ArrayAuthor
from tests.data.models.author_work_title_model import Author
from tests.data.models.basic_model import (
    BasicComplexModel,
    BasicNestedModel,
    BasicSimpleModel,
)
from tests.data.models.grouping_model import GroupingComplexModel
from tests.data.models.nested_grouping_model import NestedGroupingComplexModel
from tests.utils._types import ModelBindingsMapperParameter


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

nested_grouping_parameters = [
    ModelBindingsMapperParameter(
        model=NestedGroupingComplexModel,
        bindings=[
            {"x": 1, "y": 2, "a": "a value 1", "p": "p value 1"},
            {"x": 1, "y": 2, "a": "a value 2", "p": "p value 2"},
            {"x": 1, "y": 3, "a": "a value 3", "p": "p value 3"},
            {"x": 2, "y": 2, "a": "a value 1", "p": "p value 4"},
        ],
        expected=[
            {
                "p": "p value 1",
                "q": [{"a": "a value 1", "b": [{"x": 1, "y": 2}, {"x": 2, "y": 2}]}],
            },
            {"p": "p value 2", "q": [{"a": "a value 2", "b": [{"x": 1, "y": 2}]}]},
            {"p": "p value 3", "q": [{"a": "a value 3", "b": [{"x": 1, "y": 3}]}]},
            {
                "p": "p value 4",
                "q": [{"a": "a value 1", "b": [{"x": 1, "y": 2}, {"x": 2, "y": 2}]}],
            },
        ],
    )
]
