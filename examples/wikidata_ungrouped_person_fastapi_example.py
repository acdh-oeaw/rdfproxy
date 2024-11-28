"""RDFProxy-based FastAPI route example: Wikidata query with simple ungrouped model."""

from typing import Annotated

from fastapi import FastAPI
from pydantic import BaseModel
from rdfproxy import Page, SPARQLBinding, SPARQLModelAdapter


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
    name: str
    work: Work


adapter = SPARQLModelAdapter(
    target="https://query.wikidata.org/bigdata/namespace/wdq/sparql",
    query=query,
    model=Person,
)


app = FastAPI()


@app.get("/")
def base(page: int = 1, size: int = 100) -> Page[Person]:
    return adapter.query(page=page, size=size)