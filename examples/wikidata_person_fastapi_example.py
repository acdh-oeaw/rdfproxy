"""rdfproxy.SPARQLModelAdapter + FastAPI example targeting Wikidata."""

from typing import Annotated

from fastapi import FastAPI
from pydantic import BaseModel
from rdfproxy import Page, SPARQLBinding, SPARQLModelAdapter


class Work(BaseModel):
    name: Annotated[str, SPARQLBinding("title")]


class Person(BaseModel):
    name: str
    work: Work


query = """
SELECT ?name ?title
WHERE {
   wd:Q44336 wdt:P1559 ?name .
   wd:Q44336 wdt:P800 ?work .
   ?work wdt:P1476 ?title .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
"""

adapter = SPARQLModelAdapter(
    target="https://query.wikidata.org/bigdata/namespace/wdq/sparql",
    query=query,
    model=Person,
)


app = FastAPI()


@app.get("/")
def base() -> list[Person]:
    return adapter.query()


@app.get("/group/")
def group(group_by: str) -> dict[str, list[Person]]:
    return adapter.query(group_by=group_by)


@app.get("/paginate/")
def paginate(page: int, size: int) -> Page[Person]:
    return adapter.query(page=page, size=size)


@app.get("/grouped_paginate/")
def grouped_paginate(page: int, size: int, group_by: str) -> Page[Person]:
    return adapter.query(page=page, size=size, group_by=group_by)
