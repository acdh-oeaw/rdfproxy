"""RDFProxy-based FastAPI route example: Wikidata query with simple grouped model."""

from typing import Annotated

from fastapi import FastAPI, Query
from pydantic import BaseModel, ConfigDict
from rdfproxy import Page, QueryParameters, SPARQLBinding, SPARQLModelAdapter


query = """
SELECT ?name ?title
WHERE {
   wd:Q44336 wdt:P1559 ?name .
   wd:Q44336 wdt:P800 ?work .
   ?work wdt:P1476 ?title .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
"""


class Work(BaseModel):
    name: Annotated[str, SPARQLBinding("title")]


class Person(BaseModel):
    model_config = ConfigDict(group_by="name")

    name: str
    work: list[Work]


adapter = SPARQLModelAdapter(
    target="https://query.wikidata.org/bigdata/namespace/wdq/sparql",
    query=query,
    model=Person,
)


app = FastAPI()


@app.get("/")
def base_route(query_parameters: Annotated[QueryParameters, Query()]) -> Page[Person]:
    return adapter.query(query_parameters)
