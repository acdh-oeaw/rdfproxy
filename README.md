# RDFProxy

![tests](https://github.com/acdh-oeaw/rdfproxy/actions/workflows/tests.yaml/badge.svg)
[![coverage](https://coveralls.io/repos/github/acdh-oeaw/rdfproxy/badge.svg?branch=main&kill_cache=1)](https://coveralls.io/github/acdh-oeaw/rdfproxy?branch=main&kill_cache=1)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A collection of Python utilities for connecting an RDF store to FastAPI.


## SPARQLModelAdapter

The `rdfproxy.SPARQLModelAdapter` class allows one to run a query against an endpoint, map a flat SPARQL query result set to a potentially nested Pydantic model and optionally paginate and/or group the results by a SPARQL binding.


### SPARQL result set to Pydantic model mapping

The result set of the following query

```sparql
select ?x ?y ?a ?p
where {
  values (?x ?y ?a ?p) {
    (1 2 "a value 1" "p value 1")
    (1 22 "a value 2" "p value 2")
    (1 222 "a value 3" "p value 3")
    (2 3 "a value 4" "p value 4")
    (2 33 "a value 5" "p value 5")
    (3 4 "a value 6" "p value 6")
    (4 5 "a value 7" "p value 7")
  }
}
```

can be run against an endpoint and mapped to a nested Pydantic model like so:

```python
from pydantic import BaseModel
from rdfproxy import SPARQLModelAdapter

query = """
select ?x ?y ?a ?p
where {
  values (?x ?y ?a ?p) {
    (1 2 "a value 1" "p value 1")
    (1 22 "a value 2" "p value 2")
    (1 222 "a value 3" "p value 3")
    (2 3 "a value 4" "p value 4")
    (2 33 "a value 5" "p value 5")
    (3 4 "a value 6" "p value 6")
    (4 5 "a value 7" "p value 7")
  }
}
"""

class SimpleModel(BaseModel):
    x: int
    y: int

class NestedModel(BaseModel):
    a: str
    b: SimpleModel

class ComplexModel(BaseModel):
    p: str
    q: NestedModel

adapter = SPARQLModelAdapter(
    target="https://query.wikidata.org/bigdata/namespace/wdq/sparql",
    query=query,
    model=ComplexModel,
)

models: list[ComplexModel] = adapter.query()
```

This produces a list of Pydantic model instances (which can then be served via FastAPI):

```python
[
    ComplexModel(p='p value 1', q=NestedModel(a='a value 1', b=SimpleModel(x=1, y=2))),
    ComplexModel(p='p value 2', q=NestedModel(a='a value 2', b=SimpleModel(x=1, y=22))),
    ComplexModel(p='p value 3', q=NestedModel(a='a value 3', b=SimpleModel(x=1, y=222))),
    ComplexModel(p='p value 4', q=NestedModel(a='a value 4', b=SimpleModel(x=2, y=3))),
    ComplexModel(p='p value 5', q=NestedModel(a='a value 5', b=SimpleModel(x=2, y=33))),
    ComplexModel(p='p value 6', q=NestedModel(a='a value 6', b=SimpleModel(x=3, y=4))),
    ComplexModel(p='p value 7', q=NestedModel(a='a value 7', b=SimpleModel(x=4, y=5)))
]
```

### Pagination

Results can be paginated by passing arguments to the `page` *and* `size` parameters: 

```python
pagination: Page[ComplexModel] = adapter.query(page=1, size=2)
```
This returns a generic `Page` model instance which holds the query results as well as pagination metadata: 

```python
Page(
    items = [
        ComplexModel(p='p value 1', q=NestedModel(a='a value 1', b=SimpleModel(x=1, y=2))),
        ComplexModel(p='p value 2', q=NestedModel(a='a value 2', b=SimpleModel(x=1, y=22)))
    ],
    page=1, size=2, total=7, pages=4
)
```

### Grouping

In order to group results by a SPARQL binding, supply an argument to the `group_by` parameter:

```python
models: dict[str, list[ComplexModel]] = adapter.query(group_by="x")
```

This groups the results by the "x" binding and returns a mapping of binding values and pertaining Pydantic models:

```python
{
    '1': [
        ComplexModel(p='p value 1', q=NestedModel(a='a value 1', b=SimpleModel(x=1, y=2))),
        ComplexModel(p='p value 2', q=NestedModel(a='a value 2', b=SimpleModel(x=1, y=22))),
        ComplexModel(p='p value 3', q=NestedModel(a='a value 3', b=SimpleModel(x=1, y=222)))
    ],
    '2': [
        ComplexModel(p='p value 4', q=NestedModel(a='a value 4', b=SimpleModel(x=2, y=3))),
        ComplexModel(p='p value 5', q=NestedModel(a='a value 5', b=SimpleModel(x=2, y=33)))
    ],
    '3': [
        ComplexModel(p='p value 6', q=NestedModel(a='a value 6', b=SimpleModel(x=3, y=4)))
    ],
    '4': [
        ComplexModel(p='p value 7', q=NestedModel(a='a value 7', b=SimpleModel(x=4, y=5)))
    ]
}
```

### Grouped Pagination

Also grouped pagination is available:

```python
grouped_pagination: Page[ComplexModel] = adapter.query(group_by="x", page=1, size=2)
```

In that case, the `Page` model instance gets assigned an `item` field of `dict[str, list[ComplexModel]]`:

```python
Page(
    items = {
        '1': [
            ComplexModel(p='p value 1', q=NestedModel(a='a value 1', b=SimpleModel(x=1, y=2))),
            ComplexModel(p='p value 2', q=NestedModel(a='a value 2', b=SimpleModel(x=1, y=22))),
            ComplexModel(p='p value 3', q=NestedModel(a='a value 3', b=SimpleModel(x=1, y=222)))
        ],
        '2': [
            ComplexModel(p='p value 4', q=NestedModel(a='a value 4', b=SimpleModel(x=2, y=3))),
            ComplexModel(p='p value 5', q=NestedModel(a='a value 5', b=SimpleModel(x=2, y=33)))
        ],
    },
    page=1, size=2, total=4, pages=2
)
```
