"""SPARQLModelAdapter class for QueryResult to Pydantic model conversions."""

from collections.abc import Sequence

from SPARQLWrapper import JSON, QueryResult, SPARQLWrapper
from pydantic import BaseModel
from sparql_fastapi.utils._types import _TModelConstructorCallable
from sparql_fastapi.utils.utils import (
    get_bindings_from_query_result,
    instantiate_model_from_kwargs,
)


class SPARQLModelAdapter[ModelType: BaseModel]:
    """Adapter/Mapper for QueryResult to Pydantic model conversions."""

    def __init__(self, sparql_wrapper: SPARQLWrapper) -> None:
        self.sparql_wrapper = sparql_wrapper

        if self.sparql_wrapper.returnFormat != "json":
            self.sparql_wrapper.setReturnFormat(JSON)

    def __call__(self, query: str, model_constructor) -> Sequence[ModelType]:
        self.sparql_wrapper.setQuery(query)
        query_result: QueryResult = self.sparql_wrapper.query()

        if isinstance(model_constructor, type(BaseModel)):
            bindings = get_bindings_from_query_result(query_result)
            models: list[ModelType] = [
                instantiate_model_from_kwargs(model_constructor, **binding)
                for binding in bindings
            ]

        elif isinstance(model_constructor, _TModelConstructorCallable):
            models: list[ModelType] = model_constructor(query_result)

        else:
            raise TypeError(
                "Argument 'model_constructor' must be a model class "
                "or a model constructor callable."
            )

        return models
