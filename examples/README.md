# RDFProxy Examples

To execute the examples, the `examples` dependency group needs to be installed:

```shell
poetry install --with examples
```

## Basic FastAPI/RDFProxy example

Run the `basic_fastapi_example` with Poetry by executing:

```shell
poetry run fastapi dev basic_fastapi_example.py
```

### Routes

- http://localhost:8000/

  `SPARQLModelAdapter.query()` maps the flat SPARQL result sets to the nested `ComplexModel` model and returns a list of `ComplexModel` instances which are then served over the FastAPI route.

  <details>
  <summary>JSON result</summary>
  
  ```json
  [
   {
      "p":"p value 1",
      "q":{
         "a":"a value 1",
         "b":{
            "x":1,
            "y":2
         }
      }
   },
   {
      "p":"p value 2",
      "q":{
         "a":"a value 2",
         "b":{
            "x":1,
            "y":22
         }
      }
   },
   {
      "p":"p value 3",
      "q":{
         "a":"a value 3",
         "b":{
            "x":1,
            "y":222
         }
      }
   },
   {
      "p":"p value 4",
      "q":{
         "a":"a value 4",
         "b":{
            "x":2,
            "y":3
         }
      }
   },
   {
      "p":"p value 5",
      "q":{
         "a":"a value 5",
         "b":{
            "x":2,
            "y":33
         }
      }
   },
   {
      "p":"p value 6",
      "q":{
         "a":"a value 6",
         "b":{
            "x":3,
            "y":4
         }
      }
   },
   {
      "p":"p value 7",
      "q":{
         "a":"a value 7",
         "b":{
            "x":4,
            "y":5
         }
      }
   }
  ]
  ```
  </details>
  
- http://localhost:8000/group/?group_by=x

  `SPARQModelAdapter.query` with the `group_by` parameter groups the result model instances according to a SPARQL binding. In this case results are grouped by the "x" binding.

  <details>
  <summary>JSON result</summary>
  
  ```json
  {
   "1":[
      {
         "p":"p value 1",
         "q":{
            "a":"a value 1",
            "b":{
               "x":1,
               "y":2
            }
         }
      },
      {
         "p":"p value 2",
         "q":{
            "a":"a value 2",
            "b":{
               "x":1,
               "y":22
            }
         }
      },
      {
         "p":"p value 3",
         "q":{
            "a":"a value 3",
            "b":{
               "x":1,
               "y":222
            }
         }
      }
   ],
   "2":[
      {
         "p":"p value 4",
         "q":{
            "a":"a value 4",
            "b":{
               "x":2,
               "y":3
            }
         }
      },
      {
         "p":"p value 5",
         "q":{
            "a":"a value 5",
            "b":{
               "x":2,
               "y":33
            }
         }
      }
   ],
   "3":[
      {
         "p":"p value 6",
         "q":{
            "a":"a value 6",
            "b":{
               "x":3,
               "y":4
            }
         }
      }
   ],
   "4":[
      {
         "p":"p value 7",
         "q":{
            "a":"a value 7",
            "b":{
               "x":4,
               "y":5
            }
         }
      }
   ]
  }
  ```
  </details>

- http://localhost:8000/paginate/?page=1&size=2

  Supplying `SPARQLModelAdapter.query` with arguments for the `page` and `size` parameters returns an `rdfproxy.Page` object (a generic model instance holding the actual results along the `items` field and also pagination metadata).
  
  <details>
  <summary>JSON result</summary>
  
  ```json
  {
   "items":[
      {
         "p":"p value 1",
         "q":{
            "a":"a value 1",
            "b":{
               "x":1,
               "y":2
            }
         }
      },
      {
         "p":"p value 2",
         "q":{
            "a":"a value 2",
            "b":{
               "x":1,
               "y":22
            }
         }
      }
   ],
   "page":1,
   "size":2,
   "total":7,
   "pages":4
  }
  ```
  </details>


- http://localhost:8000/grouped_paginate/?page=1&size=2&group_by=x

  `SPARQModelAdapter.query` with arguments for `page`/`size` parameters as well as the `group_by` parameter returns an `rdfproxy.Page` object where the `items` field points to a model grouping.
  
  <details>
  <summary>JSON result</summary>
  
  ```json
  {
   "items":{
      "2":[
         {
            "p":"p value 4",
            "q":{
               "a":"a value 4",
               "b":{
                  "x":2,
                  "y":3
               }
            }
         },
         {
            "p":"p value 5",
            "q":{
               "a":"a value 5",
               "b":{
                  "x":2,
                  "y":33
               }
            }
         }
      ],
      "1":[
         {
            "p":"p value 1",
            "q":{
               "a":"a value 1",
               "b":{
                  "x":1,
                  "y":2
               }
            }
         },
         {
            "p":"p value 2",
            "q":{
               "a":"a value 2",
               "b":{
                  "x":1,
                  "y":22
               }
            }
         },
         {
            "p":"p value 3",
            "q":{
               "a":"a value 3",
               "b":{
                  "x":1,
                  "y":222
               }
            }
         }
      ]
   },
   "page":1,
   "size":2,
   "total":4,
   "pages":2
  }
  ```
  </details>




## Basic Wikidata example

This example shows how to map SPARQL query result rows to a simpel Pydantic model and serve the results over FastAPI routes.

The example query 

```sparql
SELECT ?name ?title
WHERE {
   wd:Q44336 wdt:P1559 ?name .
   wd:Q44336 wdt:P800 ?work .
   ?work wdt:P1476 ?title .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
```

returns the following result rows

| name            | title          |
|-----------------|----------------|
| Thomas Bernhard | Der Untergeher |
| Thomas Bernhard | Auslöschung    |
| Thomas Bernhard | Korrektur      |
| Thomas Bernhard | Holzfällen     |
| Thomas Bernhard | Heldenplatz    |

which shall be mapped to the following simple model:

```python
from rdfproxy import SPARQLBinding
from pydantic import BaseModel


class Work(BaseModel):
    name: Annotated[str, SPARQLBinding("title")]

class Person(BaseModel):
    name: str
    work: Work
```

### Routes

- http://localhost:8000/

  ```json
  [
   {
      "name":"Thomas Bernhard",
      "work":{
         "name":"Der Untergeher"
      }
   },
   {
      "name":"Thomas Bernhard",
      "work":{
         "name":"Auslöschung"
      }
   },
   {
      "name":"Thomas Bernhard",
      "work":{
         "name":"Korrektur"
      }
   },
   {
      "name":"Thomas Bernhard",
      "work":{
         "name":"Holzfällen"
      }
   },
   {
      "name":"Thomas Bernhard",
      "work":{
         "name":"Heldenplatz"
      }
   }
  ]
  ```

- http://localhost:8000/paginate/?page=1&size=2

  ```json 
  {
   "items":[
      {
         "name":"Thomas Bernhard",
         "work":{
            "name":"Der Untergeher"
         }
      },
      {
         "name":"Thomas Bernhard",
         "work":{
            "name":"Auslöschung"
         }
      }
   ],
   "page":1,
   "size":2,
   "total":5,
   "pages":3
  }
  ```

- http://localhost:8000/group/?group_by=name

  ```json
  {
   "Thomas Bernhard":[
      {
         "name":"Thomas Bernhard",
         "work":{
            "name":"Der Untergeher"
         }
      },
      {
         "name":"Thomas Bernhard",
         "work":{
            "name":"Auslöschung"
         }
      },
      {
         "name":"Thomas Bernhard",
         "work":{
            "name":"Korrektur"
         }
      },
      {
         "name":"Thomas Bernhard",
         "work":{
            "name":"Holzfällen"
         }
      },
      {
         "name":"Thomas Bernhard",
         "work":{
            "name":"Heldenplatz"
         }
      }
   ]
  }
  ```

- http://localhost:8000/grouped_paginate/?page=1&size=2&group_by=name

  ```json
  {
   "items":{
      "Thomas Bernhard":[
         {
            "name":"Thomas Bernhard",
            "work":{
               "name":"Der Untergeher"
            }
         },
         {
            "name":"Thomas Bernhard",
            "work":{
               "name":"Auslöschung"
            }
         },
         {
            "name":"Thomas Bernhard",
            "work":{
               "name":"Korrektur"
            }
         },
         {
            "name":"Thomas Bernhard",
            "work":{
               "name":"Holzfällen"
            }
         },
         {
            "name":"Thomas Bernhard",
            "work":{
               "name":"Heldenplatz"
            }
         }
      ]
   },
   "page":1,
   "size":2,
   "total":1,
   "pages":1
  }
  ```
