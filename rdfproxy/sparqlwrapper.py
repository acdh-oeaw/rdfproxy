from collections.abc import Iterator

import httpx


class SPARQLWrapper:
    """Simple httpx-based SPARQLWrapper implementaton for RDFProxy."""

    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    def query(self, query: str) -> Iterator[dict[str, str]]:
        """Run a SPARQL query against endpoint and return an Iterator of flat result mappings."""
        result: httpx.Response = self._httpx_run_sparql_query(query)
        return self._get_bindings_from_json_response(result.json())

    @staticmethod
    def _get_bindings_from_json_response(json_response: dict) -> Iterator[dict]:
        """Get flat dicts from a SPARQL SELECT JSON response."""
        variables = json_response["head"]["vars"]
        response_bindings = json_response["results"]["bindings"]

        bindings = (
            {var: binding.get(var, {}).get("value") for var in variables}
            for binding in response_bindings
        )

        return bindings

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
