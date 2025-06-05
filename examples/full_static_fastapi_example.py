"""RDFProxy-based FastAPI route example: Static query targeting Wikidata with grouped and nested models."""

from typing import Annotated

from pydantic import BaseModel

from fastapi import FastAPI, Query
from rdfproxy import (
    ConfigDict,
    Page,
    QueryParameters,
    SPARQLBinding,
    SPARQLModelAdapter,
)


query = """
select *
where {
    values (?gnd ?authorName ?educatedAt ?workName ?work ?viaf) {
        (119359464 'Schindel' UNDEF 'Gebürtig' <http://www.wikidata.org/entity/Q1497409> UNDEF)
        (115612815 'Geiger' 'University of Vienna' 'Der alte König in seinem Exil' <http://www.wikidata.org/entity/Q15805238> '299260555')
        (115612815 'Geiger' 'University of Vienna' 'Der alte König in seinem Exil' <http://www.wikidata.org/entity/Q15805238> '6762154387354230970008')
        (115612815 'Geiger' 'University of Vienna' 'Unter der Drachenwand' <http://www.wikidata.org/entity/Q58038819> '2277151717053313900002')
        (1136992030 'Edelbauer' 'University of Vienna' 'Das flüssige Land' <http://www.wikidata.org/entity/Q100266054> UNDEF)
        (1136992030 'Edelbauer' 'University of Applied Arts Vienna' 'Das flüssige Land' <http://www.wikidata.org/entity/Q100266054> UNDEF)
    }
}
"""


class Work(BaseModel):
    model_config = ConfigDict(group_by="name")

    name: Annotated[str, SPARQLBinding("workName")]
    viafs: Annotated[list[str], SPARQLBinding("viaf")]


class Author(BaseModel):
    model_config = ConfigDict(group_by="surname")

    gnd: int
    surname: Annotated[str, SPARQLBinding("authorName")]
    works: list[Work]
    education: Annotated[list[str], SPARQLBinding("educatedAt")]


adapter = SPARQLModelAdapter(
    target="https://query.wikidata.org/bigdata/namespace/wdq/sparql",
    query=query,
    model=Author,
)

app = FastAPI()


@app.get("/persons/")
def base_route(
    query_parameters: Annotated[QueryParameters[Author], Query()],
) -> Page[Author]:
    return adapter.get_page(query_parameters)


@app.get("/person/gnd/{gnd}")
def person_detail(gnd: int) -> Author:
    return adapter.get_item(gnd=gnd)


@app.get("/person/surname/{surname}")
def person_surname(surname: str) -> Author:
    return adapter.get_item(surname=surname)
