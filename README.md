# RDFProxy

![tests](https://github.com/acdh-oeaw/rdfproxy/actions/workflows/tests.yaml/badge.svg)
[![coverage](https://coveralls.io/repos/github/acdh-oeaw/rdfproxy/badge.svg?branch=main&kill_cache=1)](https://coveralls.io/github/acdh-oeaw/rdfproxy?branch=main&kill_cache=1)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Functionality for mapping SPARQL result sets to Pydantic models.


## SPARQLModelAdapter

The `rdfproxy.SPARQLModelAdapter` class allows to run a query against an endpoint and map a flat SPARQL query result set to a potentially nested Pydantic model.
The result is returned as a `Page` object.

The following example query

```sparql
select *
where {
    values (?gnd ?authorName ?educatedAt ?workName ?work ?viaf) {
        (119359464 'Schindel' UNDEF 'Gebürtig' <http://www.wikidata.org/entity/Q1497409> UNDEF)
        (115612815 'Geiger' 'University of Vienna' 'Der alte König in seinem Exil' <http://www.wikidata.org/entity/Q15805238> 299260555)
        (115612815 'Geiger' 'University of Vienna' 'Der alte König in seinem Exil' <http://www.wikidata.org/entity/Q15805238> 6762154387354230970008)
        (115612815 'Geiger' 'University of Vienna' 'Unter der Drachenwand' <http://www.wikidata.org/entity/Q58038819> 2277151717053313900002)
        (1136992030 'Edelbauer' 'University of Vienna' 'Das flüssige Land' <http://www.wikidata.org/entity/Q100266054> UNDEF)
        (1136992030 'Edelbauer' 'University of Applied Arts Vienna' 'Das flüssige Land' <http://www.wikidata.org/entity/Q100266054> UNDEF)
    }
}
```

retrieves the result set:

| gnd        | nameLabel | educated_atLabel                  | work_name                     | work                                      | viaf                   |
|------------|-----------|-----------------------------------|-------------------------------|-------------------------------------------|------------------------|
| 119359464  | Schindel  |                                   | Gebürtig                      | http://www.wikidata.org/entity/Q1497409   |                        |
| 115612815  | Geiger    | University of Vienna              | Der alte König in seinem Exil | http://www.wikidata.org/entity/Q15805238  | 299260555              |
| 115612815  | Geiger    | University of Vienna              | Der alte König in seinem Exil | http://www.wikidata.org/entity/Q15805238  | 6762154387354230970008 |
| 115612815  | Geiger    | University of Vienna              | Unter der Drachenwand         | http://www.wikidata.org/entity/Q58038819  | 2277151717053313900002 |
| 1136992030 | Edelbauer | University of Vienna              | Das flüssige Land             | http://www.wikidata.org/entity/Q100266054 |                        |
| 1136992030 | Edelbauer | University of Applied Arts Vienna | Das flüssige Land             | http://www.wikidata.org/entity/Q100266054 |                        |


The result set can be mapped to a nested Pydantic model like so:

```python
from typing import Annotated

from fastapi import FastAPI, Query
from pydantic import BaseModel
from rdfproxy import ConfigDict, Page, QueryParameters, SPARQLBinding, SPARQLModelAdapter

class Work(BaseModel):
    model_config = ConfigDict(group_by="name")

    name: Annotated[str, SPARQLBinding("workName")]
    viafs: Annotated[list[str], SPARQLBinding("viaf")]

class Author(BaseModel):
    model_config = ConfigDict(group_by="surname")

    gnd: str
    surname: Annotated[str, SPARQLBinding("authorName")]
    works: list[Work]
    education: Annotated[list[str], SPARQLBinding("educatedAt")]

adapter = SPARQLModelAdapter(
    target="https://query.wikidata.org/bigdata/namespace/wdq/sparql",
    query=query,
    model=Author,
)
```

The `SPARQLModelAdapter.query` method runs the query and constructs a `Page` object which can then be served over a FastAPI route:

```python
app = FastAPI()

@app.get("/")
def base_route(query_parameters: Annotated[QueryParameters, Query()]) -> Page[Author]:
    return adapter.query(query_parameters)
```

This results in the following JSON output: 

```json
{
   "items":[
      {
         "gnd":"119359464",
         "surname":"Schindel",
         "works":[
            {
               "name":"Gebürtig",
               "viafs":[
                  
               ]
            }
         ],
         "education":[
            
         ]
      },
      {
         "gnd":"115612815",
         "surname":"Geiger",
         "works":[
            {
               "name":"Der alte König in seinem Exil",
               "viafs":[
                  "299260555",
                  "6762154387354230970008"
               ]
            },
            {
               "name":"Unter der Drachenwand",
               "viafs":[
                  "2277151717053313900002"
               ]
            }
         ],
         "education":[
            "University of Vienna"
         ]
      },
      {
         "gnd":"1136992030",
         "surname":"Edelbauer",
         "works":[
            {
               "name":"Das flüssige Land",
               "viafs":[
                  
               ]
            }
         ],
         "education":[
            "University of Vienna",
            "University of Applied Arts Vienna"
         ]
      }
   ],
   "page":1,
   "size":100,
   "total":3,
   "pages":1
}
```
