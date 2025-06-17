from typing import Annotated

from fastapi import FastAPI, Query
from pydantic import AnyUrl, BaseModel
from rdfproxy import (
    ConfigDict,
    Page,
    QueryParameters,
    SPARQLBinding,
    SPARQLModelAdapter,
)


query = """
PREFIX aaao: <https://ontology.swissartresearch.net/aaao/>
PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
PREFIX lrmoo: <http://iflastandards.info/ns/lrm/lrmoo/>
PREFIX rdfschema: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX star: <https://r11.eu/ns/star/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX r11: <https://r11.eu/ns/spec/>
PREFIX r11pros: <https://r11.eu/ns/prosopography/>


SELECT
  ?Person
    ?Person_person_display_name
    ?Person_person_id_assignment
      ?Person_person_id_assignment_person_id_assignment_identifier
      ?Person_person_id_assignment_external_authority

WHERE {

  ?Person a crm:E21_Person .

  OPTIONAL {
    ?Person rdfschema:label ?Person_person_display_name .
  }

  OPTIONAL {
    ?Person a crm:E21_Person .
    ?Person ^crm:P140_assigned_attribute_to ?Person_person_id_assignment .
    ?Person_person_id_assignment a crm:E15_Identifier_Assignment .

    OPTIONAL {
      ?Person a crm:E21_Person .
      ?Person ^crm:P140_assigned_attribute_to ?Person_person_id_assignment .
      ?Person_person_id_assignment a crm:E15_Identifier_Assignment .
      ?Person_person_id_assignment crm:P37_assigned ?Person_person_id_assignment_person_id_assignment_identifier .
      ?Person_person_id_assignment_person_id_assignment_identifier a crm:E42_Identifier .
    }

    OPTIONAL {
      ?Person a crm:E21_Person .
      ?Person ^crm:P140_assigned_attribute_to ?Person_person_id_assignment .
      ?Person_person_id_assignment a crm:E15_Identifier_Assignment .
      ?Person_person_id_assignment crm:P14_carried_out_by ?Person_person_id_assignment_external_authority .
      ?Person_person_id_assignment_external_authority a lrmoo:F11_Corporate_Body .
    }
  }

}
"""


class IdentityInOtherServices(BaseModel):
    model_config = ConfigDict(
        title="",
    )
    id: Annotated[AnyUrl | None, SPARQLBinding("Person_person_id_assignment")] = None

    person_id_assignment_identifier: Annotated[
        AnyUrl | None,
        SPARQLBinding("Person_person_id_assignment_person_id_assignment_identifier"),
    ] = None
    person_id_assignment_by: Annotated[
        AnyUrl | None, SPARQLBinding("Person_person_id_assignment_external_authority")
    ] = None


class Person(BaseModel):
    model_config = ConfigDict(
        title="",
        group_by="id",
    )
    id: Annotated[AnyUrl, SPARQLBinding("Person")]

    person_display_name: Annotated[
        str | None, SPARQLBinding("Person_person_display_name")
    ] = None
    person_id_assignment: Annotated[
        list[IdentityInOtherServices], SPARQLBinding("Person_person_id_assignment")
    ]


app = FastAPI()


@app.get("/person")
def releven_person(params: Annotated[QueryParameters[Person], Query()]) -> Page[Person]:
    adapter = SPARQLModelAdapter(
        target="https://graphdb.r11.eu/repositories/RELEVEN_2025",
        query=query,
        model=Person,
    )

    return adapter.get_page(params)
