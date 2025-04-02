from collections.abc import Iterator
from typing import Any

import httpx
from rdflib import BNode, Literal, URIRef, XSD


class SPARQLWrapper:
    """Simple httpx-based SPARQLWrapper implementaton for RDFProxy."""

    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    def query(self, query: str) -> Iterator[dict[str, Any]]:
        """Run a SPARQL query against endpoint and return an Iterator of flat result mappings."""
        result: httpx.Response = self._httpx_run_sparql_query(query)
        result.raise_for_status()

        return self._get_bindings_from_json_response(result.json())

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
