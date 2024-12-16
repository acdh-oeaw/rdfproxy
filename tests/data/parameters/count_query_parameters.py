from pydantic import BaseModel
from rdfproxy import ConfigDict
from tests.utils._types import CountQueryParameter


class Dummy(BaseModel):
    pass


class GroupedDummy(BaseModel):
    model_config = ConfigDict(group_by="x")

    x: int


construct_count_query_parameters = [
    CountQueryParameter(
        query="""
        select ?x ?y ?z
        where {
            values (?x ?y ?z) {
                (1 2 3)
                (1 22 33)
                (2 222 333)
            }
        }
        """,
        model=Dummy,
        expected=3,
    ),
    CountQueryParameter(
        query="""
        select ?x ?y ?z
        where {
            values (?x ?y ?z) {
                (1 2 3)
                (1 22 33)
                (2 222 333)
            }
        }
        """,
        model=GroupedDummy,
        expected=2,
    ),
    CountQueryParameter(
        query="""
        select ?x ?y ?z
        where {
            values (?x ?y ?z) {
                (1 2 3)
                (1 22 33)
                (1 22 33)
                (2 222 333)
            }
        }
        """,
        model=Dummy,
        expected=4,
    ),
    CountQueryParameter(
        query="""
        select ?x ?y ?z
        where {
            values (?x ?y ?z) {
                (1 2 3)
                (1 22 33)
                (1 22 33)
                (2 222 333)
            }
        }
        """,
        model=GroupedDummy,
        expected=2,
    ),
    CountQueryParameter(
        query="""
        select ?x ?y ?z
        where {
            values (?x ?y ?z) {
                (1 2 3)
                (1 22 33)
                (2 222 333)
                (2 222 333)
            }
        }
        """,
        model=Dummy,
        expected=4,
    ),
    CountQueryParameter(
        query="""
        select ?x ?y ?z
        where {
            values (?x ?y ?z) {
                (1 2 3)
                (1 22 33)
                (2 222 333)
                (2 222 333)
            }
        }
        """,
        model=GroupedDummy,
        expected=2,
    ),
]
