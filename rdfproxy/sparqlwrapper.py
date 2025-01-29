from collections.abc import Iterator

import httpx


class SPARQLWrapper:
    """Simple httpx-based SPARQLWrapper implementaton for RDFProxy."""

    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    def query(self, query: str) -> Iterator[dict[str, str]]:
        """Run a SPARQL query against endpoint and return an Iterator of flat result mappings."""
        result: httpx.Response = self._httpx_run_sparql_query(query)
        return self._get_bindings_from_bindings_dict(result.json())

    @staticmethod
    def _get_bindings_from_bindings_dict(bindings_dict: dict) -> Iterator[dict]:
        bindings = map(
            lambda binding: {k: v["value"] for k, v in binding.items()},
            bindings_dict["results"]["bindings"],
        )
        return bindings

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
