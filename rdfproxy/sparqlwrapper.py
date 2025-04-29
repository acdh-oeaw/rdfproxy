import asyncio
from collections.abc import Iterator
import json
from typing import Any

import httpx
from rdflib import BNode, Graph, Literal, URIRef, XSD
from rdflib.query import Result as RDFLibQueryResult
from rdfproxy.utils.utils import compose_left


class SPARQLWrapper:
    """Simple httpx-based SPARQLWrapper implementaton for RDFProxy."""

    def __init__(self, target: str | Graph):
        self.target = target

    def queries(self, *queries: str) -> list[Iterator[dict[str, Any]]]:
        """Synchronous wrapper for asynchronous SPARQL query execution.

        SPARQLWrapper.queries takes multiple SPARQL queries, runs them
        against a service and returns a list of result iterators.
        """
        if isinstance(self.target, Graph):
            queries_coroutine = self._aqueries_graph_object
        elif isinstance(self.target, str):
            queries_coroutine = self._aqueries_remote_endpoint
        else:  # pragma: no cover
            raise TypeError("Parameter 'target' expects argument of type str | Graph.")

        return asyncio.run(queries_coroutine(*queries))

    async def _aqueries_remote_endpoint(
        self, *queries: str
    ) -> list[Iterator[dict[str, Any]]]:
        """Coroutine for running multiple queries against a remote target."""
        assert isinstance(self.target, str)  # type narrow

        async with httpx.AsyncClient() as aclient, asyncio.TaskGroup() as tg:
            tasks = [
                tg.create_task(
                    aclient.post(
                        self.target,
                        data={"output": "json", "query": query},
                        headers={
                            "Accept": "application/sparql-results+json",
                        },
                    )
                )
                for query in queries
            ]

        results: list[httpx.Response] = [task.result() for task in tasks]

        python_results = map(
            compose_left(httpx.Response.json, self._get_bindings_from_json_response),
            results,
        )

        return list(python_results)

    @staticmethod
    async def _agraph_query(graph: Graph, query: str) -> RDFLibQueryResult:
        """Thin async-thread wrapper for rdflib.Graph.query."""
        return await asyncio.to_thread(graph.query, query)

    async def _aqueries_graph_object(
        self, *queries: str
    ) -> list[Iterator[dict[str, Any]]]:
        """Coroutine for running multiple queries against an rdflib.Graph target.

        Note that _aquery_graph_object wraps rdflib.Graph.query
        in a separate thread using asyncio.to_thread.
        """
        assert isinstance(self.target, Graph)  # type narrow

        tasks = [self._agraph_query(self.target, query) for query in queries]
        results: list[RDFLibQueryResult] = await asyncio.gather(*tasks)

        python_results = map(
            compose_left(
                lambda result: result.serialize(format="json"),
                json.loads,
                self._get_bindings_from_json_response,
            ),
            results,
        )

        return list(python_results)

    @staticmethod
    def _get_bindings_from_json_response(
        json_response: dict[str, Any],
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
