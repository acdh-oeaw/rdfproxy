"""A somewhat abstract example of the model_bool config option for aggregation and model union fields."""

from typing import Annotated

from fastapi import FastAPI, Query
from pydantic import BaseModel
from rdfproxy import ConfigDict, Page, QueryParameters, SPARQLModelAdapter


query = """
select *
where {
    values (?x ?y) {
        (1 2)
        (1 3)
        (2 undef)
    }
}
"""


class Nested(BaseModel):
    model_config = ConfigDict(model_bool="y")

    y: int | None
    z: int = 3


class Model(BaseModel):
    model_config = ConfigDict(group_by="x")

    x: int
    y: list[int]
    model_union: Nested | str = "default"
    model_aggregation: list[Nested]


adapter = SPARQLModelAdapter(
    target="https://query.wikidata.org/bigdata/namespace/wdq/sparql",
    query=query,
    model=Model,
)

app = FastAPI()


@app.get("/")
def base_route(
    query_parameters: Annotated[QueryParameters[Model], Query()],
) -> Page[Model]:
    return adapter.get_page(query_parameters)
