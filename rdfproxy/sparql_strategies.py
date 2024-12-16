"""Strategy classes for SPARQL query functionality."""

import abc
from collections.abc import Iterator
from typing import cast

from SPARQLWrapper import JSON, QueryResult, SPARQLWrapper
import httpx


class SPARQLStrategy(abc.ABC):
    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    @abc.abstractmethod
    def query(self, sparql_query: str) -> Iterator[dict[str, str]]:
        raise NotImplementedError  # pragma: no cover

    @staticmethod
    def _get_bindings_from_bindings_dict(bindings_dict: dict) -> Iterator[dict]:
        bindings = map(
            lambda binding: {k: v["value"] for k, v in binding.items()},
            bindings_dict["results"]["bindings"],
        )
        return bindings


class SPARQLWrapperStrategy(SPARQLStrategy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._sparql_wrapper = SPARQLWrapper(self.endpoint)
        self._sparql_wrapper.setReturnFormat(JSON)

    def query(self, sparql_query: str) -> Iterator[dict[str, str]]:
        self._sparql_wrapper.setQuery(sparql_query)

        result: QueryResult = self._sparql_wrapper.query()
        # SPARQLWrapper.Wrapper.convert is not overloaded properly and needs casting
        # https://github.com/RDFLib/sparqlwrapper/blob/master/SPARQLWrapper/Wrapper.py#L1135
        return self._get_bindings_from_bindings_dict(cast(dict, result.convert()))


class HttpxStrategy(SPARQLStrategy):
    def query(self, sparql_query: str) -> Iterator[dict[str, str]]:
        result: httpx.Response = self._httpx_run_sparql_query(sparql_query)
        return self._get_bindings_from_bindings_dict(result.json())

    def _httpx_run_sparql_query(self, query: str) -> httpx.Response:
        data = {"output": "json", "query": query}
        headers = {
            "Accept": "application/sparql-results+json",
        }

        response = httpx.post(
            self.endpoint,
            headers=headers,
            data=data,
        )

        return response
