# RDFProxy

![tests](https://github.com/acdh-oeaw/rdfproxy/actions/workflows/tests.yaml/badge.svg)
[![coverage](https://coveralls.io/repos/github/acdh-oeaw/rdfproxy/badge.svg?branch=main&kill_cache=1)](https://coveralls.io/github/acdh-oeaw/rdfproxy?branch=main&kill_cache=1)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A collection of Python utilities for connecting an RDF store to FastAPI.


## SPARQLModelAdapter

The `rdfproxy.SPARQLModelAdapter` class allows to run a query against an endpoint and map a flat SPARQL query result set to a potentially nested Pydantic model.

E.g. the result set of the following query
```sparql
select ?x ?y ?a ?p
where {
    values (?x ?y ?a ?p) {
        (1 2 "a value" "p value")
    }
}
```
can be run against an endpoint and mapped to a nested Pydantic model like so:

```python
from SPARQLWrapper import SPARQLWrapper
from pydantic import BaseModel
from rdfproxy import SPARQLModelAdapter, _TModelInstance

class SimpleModel(BaseModel):
    x: int
    y: int

class NestedModel(BaseModel):
    a: str
    b: SimpleModel

class ComplexModel(BaseModel):
    p: str
    q: NestedModel


sparql_wrapper = SPARQLWrapper("https://query.wikidata.org/bigdata/namespace/wdq/sparql")

query = """
select ?x ?y ?a ?p
where {
    values (?x ?y ?a ?p) {
        (1 2 "a value" "p value")
    }
}
"""

adapter = SPARQLModelAdapter(sparql_wrapper=sparql_wrapper)
models: list[_TModelInstance] = adapter(query=query, model_constructor=ComplexModel)
```

This produces an Iterable of Pydantic model instances (in the above case: `[ComplexModel(p='p value', q=NestedModel(a='a value', b=SimpleModel(x=1, y=2)))]`) which can then be served via FastAPI.

The `model_constructor` parameter takes either a Pydantic model directly or a model_constructor callable which receives the raw `SPARQLWrapper.QueryResult` object and is responsible for returning an Iterable of model instances.

