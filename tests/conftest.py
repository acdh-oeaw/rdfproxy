"""Pytest fixture definitions."""

from collections.abc import Iterator
import time
from typing import Protocol

import httpx
import pytest
from rdflib import Graph
from rdfproxy.sparqlwrapper import SPARQLWrapper
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs


class _Endpoints(Protocol):
    sparql_endpoint: str
    update_endpoint: str
    graphstore_endpoint: str

    def __iter__(self) -> Iterator[str]:
        yield from (
            self.sparql_endpoint,
            self.update_endpoint,
            self.graphstore_endpoint,
        )


class OxiGraphEndpoints(_Endpoints):
    """Data Container for Oxigraph SPARQL and Graphstore Endpoints.

    Endpoints are computed given a host and port.
    The class implements the Iterable protocol for unpacking.
    """

    def __init__(self, host, port):
        self._endpoint_base = f"http://{host}:{port}"

        self.sparql_endpoint = f"{self._endpoint_base}/query"
        self.update_endpoint = f"{self._endpoint_base}/update"
        self.graphstore_endpoint = f"{self._endpoint_base}/store"


def wait_for_service(url: str, attempts: int = 10) -> None:
    for _ in range(attempts):
        try:
            response = httpx.get(url)
            if response.status_code == 200:
                break
        except httpx.RequestError:
            time.sleep(1)
        else:
            raise RuntimeError(
                f"Requested service at {url} "
                f"did not become available after {attempts} attempts."
            )


@pytest.fixture(scope="session")
def oxigraph_service() -> Iterator[OxiGraphEndpoints]:
    with DockerContainer("oxigraph/oxigraph").with_exposed_ports(7878) as container:
        host = container.get_container_host_ip()
        port = container.get_exposed_port(7878)

        endpoints: _Endpoints = OxiGraphEndpoints(host=host, port=port)

        wait_for_service(endpoints.sparql_endpoint, attempts=10)
        yield endpoints


class FusekiEndpoints(_Endpoints):
    """Data Container for Fuseki SPARQL and Graphstore Endpoints.

    Endpoints are computed given a host and port.
    The class implements the Iterable protocol for unpacking.
    """

    def __init__(self, host, port):
        self._endpoint_base = f"http://{host}:{port}/ds"

        self.sparql_endpoint = f"{self._endpoint_base}/sparql"
        self.update_endpoint = f"{self._endpoint_base}/update"
        self.graphstore_endpoint = f"{self._endpoint_base}/data"


@pytest.fixture(scope="session")
def fuseki_service() -> Iterator[FusekiEndpoints]:
    """Fixture that starts a Fuseki Triplestore container and exposes an Endpoint object."""
    with (
        DockerContainer("secoresearch/fuseki")
        .with_exposed_ports(3030)
        .with_env("ENABLE_DATA_WRITE", "true")
        .with_env("ENABLE_UPDATE", "true")
    ) as container:
        wait_for_logs(container, "Start Fuseki")

        host = container.get_container_host_ip()
        port = container.get_exposed_port(3030)

        endpoints = FusekiEndpoints(host=host, port=port)
        yield endpoints


@pytest.fixture(params=["rdflib", "oxigraph_service", "fuseki_service"])
def target(request) -> Graph | str:
    """SPARQLEndpoint target fixture.

    Note: The fixture dynamically fetches endpoint service fixtures from its parameters.
    """

    if request.param == "rdflib":
        return Graph()

    endpoints = request.getfixturevalue(request.param)
    return endpoints.sparql_endpoint


@pytest.fixture()
def sparql_wrapper(target) -> SPARQLWrapper:
    """SPARQLWrapper instance fixture."""
    return SPARQLWrapper(target=target)
