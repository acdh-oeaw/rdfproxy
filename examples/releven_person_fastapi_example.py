"""RDFProxy-based FastAPI route example: CRM query targeting Releven GraphDB with simple ungrouped Person model."""

from typing import Annotated

from fastapi import FastAPI, Query
from pydantic import BaseModel
from rdfproxy import Page, QueryParameters, SPARQLModelAdapter


query = """
PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
PREFIX star: <https://r11.eu/ns/star/>

select ?id_content ?id_note ?appellation_content ?note
where {

    ?person a crm:E21_Person .

  {
    # id
    ?person ^crm:P140_assigned_attribute_to ?e13_id .
    ?e13_id a crm:E15_Identifier_Assignment ;
    crm:P37_assigned [
		a crm:E42_Identifier ;
		crm:P190_has_symbolic_content ?id_content ;
		crm:P3_has_note ?id_note
	] .
    filter (?id_content != ?id_note)
  }

  {
    # appellation
    ?person ^crm:P140_assigned_attribute_to ?e13_appellation .

    ?e13_appellation a star:E13_crm_P1 ;
    crm:P141_assigned [
		a crm:E41_Appellation ;
		crm:P190_has_symbolic_content ?appellation_content
		] .
  }

  {
    # note
    ?person ^crm:P140_assigned_attribute_to ?e13_note .

    ?e13_note a star:E13_crm_P3 ;
    	crm:P141_assigned ?note .
  }
}

"""


class R11PersonModel(BaseModel):
    id_content: str
    id_note: str
    appellation_content: str
    note: str


adapter = SPARQLModelAdapter(
    target="https://graphdb.r11.eu/repositories/RELEVEN",
    query=query,
    model=R11PersonModel,
)

app = FastAPI()


@app.get("/")
def base_route(
    query_parameters: Annotated[QueryParameters[R11PersonModel], Query()],
) -> Page[R11PersonModel]:
    return adapter.query(query_parameters)
