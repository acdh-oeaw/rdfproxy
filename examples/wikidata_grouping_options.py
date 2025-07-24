"""RDFProxy-based FastAPI route example: Wikidata query with simple grouped model."""

from typing import Annotated

from fastapi import FastAPI, Query
from pydantic import BaseModel
from rdfproxy import (
    ConfigDict,
    Page,
    QueryParameters,
    SPARQLBinding,
    SPARQLModelAdapter,
)


# the child Label isn't used in most models -- it doesn't matter if it's in the SELECT anyway since it doesn't change the number of rows of the result
query = """
SELECT ?husbandLabel ?wifeLabel ?childLabel ?childBirthplaceLabel WHERE {
   VALUES ?husband {wd:Q1339 wd:Q75925 }

  ?husband wdt:P26 ?wife.
  ?husband wdt:P40 ?child.
  ?wife wdt:P40 ?child.
  ?child wdt:P19 ?childBirthplace.
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],mul,en". }
}
"""



def get_adapter(model):
    return SPARQLModelAdapter(
        target="https://query.wikidata.org/bigdata/namespace/wdq/sparql",
        query=query,
        model=model,
    )


app = FastAPI()

# the SPARQL result has 20 rows, each giving 3 basic items: husband, wife, child. those 3 items can be structured into models in 7 possible ways:

# 1. .. no structuring, just flat husband/wife/child triples: produces 20 models
# 2. N. a single level of nesting, produces 20 models
# 3. NN two levels of nesting, produces 20 models
# 4. G. a single level of grouping
# 5. GG two levels of grouping (each husband's wives, and the children with each)
# 6. GN a single level of grouping, followed by nested model
# 7. NG a nested model, with a grouping inside it


# fine
class NoStructuring(BaseModel):
    childLabel: str
    husbandLabel: str
    wifeLabel: str

@app.get("/1_flat")
def base_route(
    query_parameters: Annotated[QueryParameters[NoStructuring], Query()],
) -> Page[NoStructuring]:
    return get_adapter(NoStructuring).get_page(query_parameters)



# fine
class Parents(BaseModel):
    husbandLabel: str
    wifeLabel: str

class ChildBirthsAndTheirParents(BaseModel):
    childLabel: str
    parents: Parents

@app.get("/2_nested")
def base_route(
    query_parameters: Annotated[QueryParameters[ChildBirthsAndTheirParents], Query()],
) -> Page[ChildBirthsAndTheirParents]:
    return get_adapter(ChildBirthsAndTheirParents).get_page(query_parameters)


# fine
class Husband(BaseModel):
    husbandLabel: str

class Marriage(BaseModel):
    wifeLabel: str
    husband: Husband

class ChildBirthsAndTheirMarriages(BaseModel):
    childLabel: str
    marriage: Marriage

@app.get("/3_nested_nested")
def base_route(
    query_parameters: Annotated[QueryParameters[ChildBirthsAndTheirMarriages], Query()],
) -> Page[ChildBirthsAndTheirMarriages]:
    return get_adapter(ChildBirthsAndTheirMarriages).get_page(query_parameters)



# routes below here have broken 'total' count

# fine BUT ideally we want to group after both wifeLabel and husbandLabel??
class MarriageAndItsChildren(BaseModel):
    model_config = ConfigDict(group_by="wifeLabel")
    husbandLabel: str
    wifeLabel: str
    children: Annotated[list[str], SPARQLBinding("childLabel")]

@app.get("/4_groupedprimitive")
def base_route(
    query_parameters: Annotated[QueryParameters[MarriageAndItsChildren], Query()],
) -> Page[MarriageAndItsChildren]:
    return get_adapter(MarriageAndItsChildren).get_page(query_parameters)



# fine
class ChildAndItsParents(BaseModel):
    childLabel: str
    husbandLabel: str
    wifeLabel: str

class BirthplacesAndTheirChildren(BaseModel):
    model_config = ConfigDict(group_by="childBirthplaceLabel")
    childBirthplaceLabel: str
    nested: list[ChildAndItsParents]

@app.get("/4_grouped")
def base_route(
    query_parameters: Annotated[QueryParameters[BirthplacesAndTheirChildren], Query()],
) -> Page[BirthplacesAndTheirChildren]:
    return get_adapter(BirthplacesAndTheirChildren).get_page(query_parameters)



# fine
class HusbandAndChildren(BaseModel):
    model_config = ConfigDict(group_by="husbandLabel")
    husbandLabel: str
    childLabel: list[str]

class WivesAndTheirMarriages(BaseModel):
    model_config = ConfigDict(group_by="wifeLabel")
    wifeLabel: str
    nested: list[HusbandAndChildren]

@app.get("/5_grouped_grouped")
def base_route(
    query_parameters: Annotated[QueryParameters[WivesAndTheirMarriages], Query()],
) -> Page[WivesAndTheirMarriages]:
    return get_adapter(WivesAndTheirMarriages).get_page(query_parameters)



# fine
class ChildAndItsParents_Nested(BaseModel):
    childLabel: str
    parents: Parents

class BirthplacesAndTheirChildren_Nested(BaseModel):
    model_config = ConfigDict(group_by="childBirthplaceLabel")
    childBirthplaceLabel: str
    children: list[ChildAndItsParents_Nested]

@app.get("/6_grouped_nested")
def base_route(
    query_parameters: Annotated[QueryParameters[BirthplacesAndTheirChildren_Nested], Query()],
) -> Page[BirthplacesAndTheirChildren_Nested]:
    return get_adapter(BirthplacesAndTheirChildren_Nested).get_page(query_parameters)




# not fine: wrong result on fix/, doesn't validate on quickfix/ (grouping isn't triggered?)
class MarriageAndItsChildren_Nested(BaseModel):
    wifeLabel: str
    nested: HusbandAndChildren

@app.get("/7_nested_grouped")
def base_route(
    query_parameters: Annotated[QueryParameters[MarriageAndItsChildren_Nested], Query()],
) -> Page[MarriageAndItsChildren_Nested]:
    return get_adapter(MarriageAndItsChildren_Nested).get_page(query_parameters)

