"""Type definitions for rdfproxy."""

from collections import UserString
from typing import Generic, Protocol, TypeAlias, TypeVar, runtime_checkable

from pydantic import BaseModel, ConfigDict as PydanticConfigDict
from rdflib.plugins.sparql.parser import parseQuery
from rdflib.plugins.sparql.parserutils import CompValue
from rdfproxy.utils._exceptions import QueryParseException


_TModelInstance = TypeVar("_TModelInstance", bound=BaseModel)


class ItemsQueryConstructor(Protocol):
    def __call__(self, query: str, limit: int, offset: int) -> str: ...


class SPARQLBinding(str):
    """SPARQLBinding type for explicit SPARQL binding to model field allocation.

    This type's intended use is with typing.Annotated in the context of a Pyantic field definition.

    Example:

        class Work(BaseModel):
           name: Annotated[str, SPARQLBinding("title")]

        class Person(BaseModel):
            name: str
            work: Work

    This signals to the RDFProxy SPARQL-to-model mapping logic
    to use the "title" SPARQL binding (not the "name" binding) to populate the Work.name field.
    """

    ...


@runtime_checkable
class ModelBoolPredicate(Protocol):
    """Type for model_bool predicate functions."""

    def __call__(self, model: BaseModel) -> bool: ...


_TModelBoolValue: TypeAlias = ModelBoolPredicate | str | set[str]


class ConfigDict(PydanticConfigDict, total=False):
    """pydantic.ConfigDict extension for RDFProxy model_config options."""

    group_by: str
    model_bool: _TModelBoolValue


_TQuery = TypeVar("_TQuery", bound=str)


class ParsedSPARQL(Generic[_TQuery], UserString):
    """UserString for encapsulating parsed SPARQL queries."""

    def __init__(self, query: _TQuery) -> None:
        self.data: _TQuery = query
        self.parse_object: CompValue = self._get_parse_object(query)

    @staticmethod
    def _get_parse_object(query: str) -> CompValue:
        try:
            _parsed = parseQuery(query)
        except Exception as e:
            raise QueryParseException(e) from e
        else:
            _, parse_object = _parsed
            return parse_object
