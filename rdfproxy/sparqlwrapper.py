from collections.abc import Iterator
import json
from typing import Any, cast

from rdflib import BNode, Graph, Literal, URIRef, XSD

import httpx


class SPARQLWrapper:
    """Simple httpx-based SPARQLWrapper implementaton for RDFProxy."""

    def __init__(self, target: str | Graph):
        self.target = target

    def query(self, query: str) -> Iterator[dict[str, Any]]:
        """Run a SPARQL query against target and return an Iterator of flat result mappings."""
        if isinstance(self.target, Graph):
            return self._query_graph_object(query)
        elif isinstance(self.target, str):
            return self._query_remote_endpoint(query)
        else:  # pragma: no cover
            raise Exception("Parameter 'target' expects argument of type str | Graph.")

    def _query_remote_endpoint(self, query: str) -> Iterator[dict[str, Any]]:
        """Run a SPARQL query against a remote endpoint."""
        result: httpx.Response = self._httpx_run_sparql_query(query)
        result.raise_for_status()

        return self._get_bindings_from_json_response(result.json())

    def _query_graph_object(self, query: str) -> Iterator[dict[str, Any]]:
        """Run a SPARQL query against an rdflib.Graph instance.

        Note: rdflib.query.Result.serialize has a union return type;
        the return type can be safely cast though, because the union-relevant
        code path depends on the destination parameter, which isn't used here.
        """
        assert isinstance(self.target, Graph)  # type narrow

        _result = self.target.query(query)
        _serialized = cast(bytes, _result.serialize(format="json"))
        _result_json = json.loads(_serialized)

        return self._get_bindings_from_json_response(_result_json)

    @staticmethod
    def _get_bindings_from_json_response(
        json_response: dict,
    ) -> Iterator[dict[str, Any]]:
        """Get flat dicts from a SPARQL SELECT JSON response."""
        variables = json_response["head"]["vars"]
        response_bindings = json_response["results"]["bindings"]

        def _get_binding_pairs(binding) -> Iterator[tuple[str, Any]]:
            """Generate key value pairs from response_bindings.

            The 'type' and 'datatype' fields of the JSON response
            are examined to cast values to Python types according to RDFLib.
            """
            for var in variables:
                if (binding_data := binding.get(var, None)) is None:
                    yield (var, None)
                    continue

                match binding_data["type"]:
                    case "uri":
                        yield (var, URIRef(binding_data["value"]))
                    case "literal":
                        literal = Literal(
                            binding_data["value"],
                            datatype=binding_data.get("datatype", None),
                        )

                        # call toPython in any case for validation
                        literal_to_python = literal.toPython()

                        if literal.datatype in (XSD.gYear, XSD.gYearMonth):
                            yield (var, literal)
                        else:
                            yield (var, literal_to_python)

                    case "bnode":
                        yield (var, BNode(binding_data["value"]))
                    case _:  # pragma: no cover
                        assert False, "This should never happen."

        for binding in response_bindings:
            yield dict(_get_binding_pairs(binding))

    def _httpx_run_sparql_query(self, query: str) -> httpx.Response:
        """Run a query against endpoint using httpx.post."""
        assert isinstance(self.target, str)

        data = {"output": "json", "query": query}
        headers = {
            "Accept": "application/sparql-results+json",
        }

        response = httpx.post(
            self.target,
            headers=headers,
            data=data,
        )

        return response
