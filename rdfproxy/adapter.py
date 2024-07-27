"""SPARQLModelAdapter class for QueryResult to Pydantic model conversions."""

from collections.abc import Iterable
from typing import cast

from SPARQLWrapper import JSON, QueryResult, SPARQLWrapper
from pydantic import BaseModel

from rdfproxy.utils._types import _TModelConstructorCallable, _TModelInstance
from rdfproxy.utils.utils import (
    get_bindings_from_query_result,
    instantiate_model_from_kwargs,
)


class SPARQLModelAdapter:
    """Adapter/Mapper for QueryResult to Pydantic model conversions.

    The rdfproxy.SPARQLModelAdapter class allows to run a query against an endpoint
    and map a flat SPARQL query result set to a potentially nested Pydantic model.

    Example:

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

        query = '''
            select ?x ?y ?a ?p
            where {
                values (?x ?y ?a ?p) {
                    (1 2 "a value" "p value")
                }
            }
        '''

        adapter = SPARQLModelAdapter(sparql_wrapper=sparql_wrapper)
        models: list[_TModelInstance] = adapter(query=query, model_constructor=ComplexModel)
    """

    def __init__(self, sparql_wrapper: SPARQLWrapper) -> None:
        self.sparql_wrapper = sparql_wrapper

        if self.sparql_wrapper.returnFormat != "json":
            self.sparql_wrapper.setReturnFormat(JSON)

    def __call__(
        self,
        query: str,
        model_constructor: type[_TModelInstance] | _TModelConstructorCallable,
    ) -> Iterable[_TModelInstance]:
        self.sparql_wrapper.setQuery(query)
        query_result: QueryResult = self.sparql_wrapper.query()

        if isinstance(model_constructor, type(BaseModel)):
            model_constructor = cast(type[_TModelInstance], model_constructor)

            bindings = get_bindings_from_query_result(query_result)
            models: list[_TModelInstance] = [
                instantiate_model_from_kwargs(model_constructor, **binding)
                for binding in bindings
            ]

        elif isinstance(model_constructor, _TModelConstructorCallable):
            models: Iterable[_TModelInstance] = model_constructor(query_result)

        else:
            raise TypeError(
                "Argument 'model_constructor' must be a model class "
                "or a model constructor callable."
            )

        return models
