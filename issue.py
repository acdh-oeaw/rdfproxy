from typing import Annotated

from fastapi import FastAPI, Query
from pydantic import BaseModel
from rdfproxy import ConfigDict
from rdfproxy import Page, QueryParameters, SPARQLModelAdapter

query = """SELECT ?root ?childlist ?nested ?nestedchildlist
WHERE {

  VALUES (?root ?childlist ?nested ?nestedchildlist) {

    # nestedchildlist: Input should be a valid list [type=list_type, input_value='AC1Na', input_type=str]
    ( "A" "AC1" "AC1N" "AC1Na" )

    # same
    ( "B" "BC1" "BC1N" "BC1Na" )
    ( "B" "BC1" "BC1N" "BC2Nb" )

    # nestedchildlist: Input should be a valid list [type=list_type, input_value=None, input_type=NoneType]
    ( "C" "CC1" "CC1N" UNDEF )
  }
}"""


class Nested(BaseModel):
    model_config = ConfigDict(group_by="nested")

    nested: str
    nestedchildlist: list[str]


class Root(BaseModel):
    model_config = ConfigDict(group_by="root")

    root: str

    childlist: list[str]
    nested_model: Nested


app = FastAPI(debug=True)


@app.get("/")
def getroot(params: Annotated[QueryParameters[Root], Query()]) -> Page[Root]:
    adapter = SPARQLModelAdapter(
        target="https://graphdb.r11.eu/repositories/RELEVEN_2025",
        query=query,
        model=Root,
    )

    return adapter.get_page(params)
