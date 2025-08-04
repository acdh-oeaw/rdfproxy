"""Type definitions for rdfproxy."""

from collections import UserString
from collections.abc import Iterable
import datetime
import decimal
from typing import Generic, Protocol, TypeAlias, TypeVar, runtime_checkable
from xml.dom.minidom import Document

from pydantic import AnyUrl, BaseModel, ConfigDict as PydanticConfigDict
from rdflib import BNode, Literal, URIRef
from rdflib.compat import long_type
from rdflib.plugins.sparql.parser import parseQuery
from rdflib.plugins.sparql.parserutils import CompValue
from rdflib.xsd_datetime import Duration
from rdfproxy.utils.exceptions import QueryParseException


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
    orderable_fields: Iterable[str]


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


_TLiteralToPython: TypeAlias = (
    Literal
    | None
    | datetime.date
    | datetime.datetime
    | datetime.time
    | datetime.timedelta
    | Duration
    | bytes
    | bool
    | int
    | float
    | decimal.Decimal
    | long_type
    | Document
)
"""Return type for rdflib.Literal.toPython.

This union type represents all possible return value types of Literal.toPython.
Return type provenance:

    - Literal: rdflib.Literal.toPython
    - None: rdflib.term._castLexicalToPython
    - datetime.date: rdflib.xsd_datetime.parse_date, rdflib.xsd_datetime.parse_xsd_date
    - datetime.datetime: rdflib.xsd_datetime.parse_datetime
    - datetime.time: rdflib.xsd_datetime.parse_time
    - datetime.timedelta, Duration: parse_xsd_duration
    - bytes: rdflib.term._unhexlify, base64.b64decode
    - bool: rdflib.term._parseBoolean
    - int, float, decimal.Decimal, long_type: rdflib.term.XSDToPython
    - Document: rdflib.term._parseXML
"""


_TSPARQLBindingValue: TypeAlias = URIRef | BNode | _TLiteralToPython
"Return type for rdfproxy.SPARQLWrapper result mapping values."


_TSPARQLBoundField: TypeAlias = _TSPARQLBindingValue | AnyUrl | str
"""Return type for rdfproxy.SPARQLWrapper result mapping values AND respective Pydantic coercions.

Currently, this type is used primarily for runtime checks against FieldInfo.annotations in ModelSPARQLMap.

_TSPARQLBoundField is an extension of _TSPARQLBindingValue and aims to capture
all possible types of rdfproxy.SPARQLWrapper result dict values
and respective coercion types for Pydantic's non-strict mode.

Note that _TSPARQBoundField might be incomplete and require additional union members.
"""
