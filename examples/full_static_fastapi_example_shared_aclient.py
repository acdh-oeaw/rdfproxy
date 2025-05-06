from contextlib import asynccontextmanager
import logging
from typing import Annotated

from fastapi import FastAPI, Query
import httpx
from pydantic import BaseModel
from rdfproxy import (
    ConfigDict,
    Page,
    QueryParameters,
    SPARQLBinding,
    SPARQLModelAdapter,
)


logger = logging.getLogger("uvicorn.info")

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


aclient = httpx.AsyncClient()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("App Startup - aclient closed: %s", aclient.is_closed)
    yield
    await aclient.aclose()
    logger.info("App Shutdown - aclient closed: %s", aclient.is_closed)


adapter = SPARQLModelAdapter(
    target="https://query.wikidata.org/bigdata/namespace/wdq/sparql",
    query=query,
    model=Author,
    aclient=aclient,
)

app = FastAPI(lifespan=lifespan)


@app.get("/")
def base_route(
    query_parameters: Annotated[QueryParameters[Author], Query()],
) -> Page[Author]:
    assert adapter.sparqlwrapper.aclient.aclient == aclient
    return adapter.query(query_parameters)
