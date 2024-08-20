"""SPARQL/FastAPI utils."""

from collections.abc import Iterator
from typing import Any

from SPARQLWrapper import QueryResult
from pydantic import BaseModel
from pydantic.fields import FieldInfo
from rdfproxy.utils._types import SPARQLBinding, _TModelInstance


def get_bindings_from_query_result(query_result: QueryResult) -> Iterator[dict]:
    """Extract just the bindings from a SPARQLWrapper.QueryResult."""
    if (result_format := query_result.requestedFormat) != "json":
        raise Exception(
            "Only QueryResult objects with JSON format are currently supported. "
            f"Received object with requestedFormat '{result_format}'."
        )

    query_json: dict = query_result.convert()
    bindings = map(
        lambda binding: {k: v["value"] for k, v in binding.items()},
        query_json["results"]["bindings"],
    )

    return bindings


def instantiate_model_from_kwargs(
    model: type[_TModelInstance], **kwargs
) -> _TModelInstance:
    """Instantiate a (potentially nested) model from (flat) kwargs.

    More a more generic version of this function see upto.init_model_from_kwargs
    https://github.com/lu-pl/upto?tab=readme-ov-file#init_model_from_kwargs.

    Example:

        class SimpleModel(BaseModel):
            x: int
            y: int


        class NestedModel(BaseModel):
            a: str
            b: SimpleModel


        class ComplexModel(BaseModel):
            p: str
            q: NestedModel


    model = instantiate_model_from_kwargs(ComplexModel, x=1, y=2, a="a value", p="p value")
    print(model)  # p='p value' q=NestedModel(a='a value', b=SimpleModel(x=1, y=2))
    """

    def _get_key_from_metadata(v: FieldInfo):
        """Try to get a SPARQLBinding object from a field's metadata attribute.

        Helper for _generate_binding_pairs.
        """
        try:
            value = next(filter(lambda x: isinstance(x, SPARQLBinding), v.metadata))
            return value
        except StopIteration:
            return None

    def _generate_binding_pairs(
        model: type[_TModelInstance], **kwargs
    ) -> Iterator[tuple[str, Any]]:
        """Get the bindings needed for model instantation.

        The function traverses model.model_fields
        and constructs binding pairs by either getting values from kwargs or field defaults.
        For model fields the recursive clause runs.
        """
        for k, v in model.model_fields.items():
            if isinstance(v.annotation, type(BaseModel)):
                value = v.annotation(
                    **dict(_generate_binding_pairs(v.annotation, **kwargs))
                )
            else:
                binding_key = _get_key_from_metadata(v) or k
                value = kwargs.get(binding_key, v.default)

            yield k, value

    bindings = dict(_generate_binding_pairs(model, **kwargs))
    return model(**bindings)
