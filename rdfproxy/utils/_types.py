"""Type definitions for rdfproxy."""

from typing import TypeVar

from pydantic import BaseModel


_TModelInstance = TypeVar("_TModelInstance", bound=BaseModel)


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
