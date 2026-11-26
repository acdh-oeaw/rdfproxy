"""Regression tests for thread-safe SPARQL parsing.

pyparsing.core._trim_arity determines parse action arities lazily on first call
and caches them in closure state shared across threads; concurrent first calls
corrupt that state and permanently break RDFLib's SPARQL parser for the process.

rdfproxy parses under a lock and pre-parses every query it hands to sparqlx,
so concurrent rdfproxy usage must never hit the race, including sparqlx's own parsing.

The race only occurs on a cold parser, so every test case runs in a fresh interpreter
and releases all threads simultaneously through a barrier.
See https://github.com/erc-releven/releven-backend/issues/2.
"""

import json
import subprocess
import sys
from typing import NamedTuple

import pytest

script = """
import json
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

from pydantic import BaseModel
from rdflib import Graph

from rdfproxy import SPARQLModelAdapter
from rdfproxy.utils._types import ParsedSPARQL
from rdfproxy.utils.sparql_utils import get_query_projection, parse_query

query = '''
PREFIX ex: <http://example.org/>
SELECT ?x ?y
WHERE {
  VALUES (?x ?y) { (1 2) (3 4) }
  OPTIONAL { ?x ex:p 'a'@en }
  FILTER (?y > 0)
}
'''

class Model(BaseModel):
    x: int
    y: int

def adapter():
    return SPARQLModelAdapter(target=Graph(), query=query, model=Model)

scenarios = {
    "parse_query": lambda: parse_query(query=query),
    "ParsedSPARQL": lambda: ParsedSPARQL(query=query),
    "get_query_projection": lambda: get_query_projection(query=query),
    "get_page": lambda: adapter().get_page(),
    "get_item": lambda: adapter().get_item(x=1),
}

threads, *names = int(sys.argv[1]), *sys.argv[2:]
barrier = threading.Barrier(threads)

def work(i):
    barrier.wait()
    try:
        scenarios[names[i % len(names)]]()
    except Exception as e:
        return f"{type(e).__name__}: {e}"

with ThreadPoolExecutor(max_workers=threads) as executor:
    print(json.dumps([r for r in executor.map(work, range(threads)) if r is not None]))
"""


class ConcurrentParseParameter(NamedTuple):
    scenarios: tuple[str, ...]
    threads: int = 32


params: list[ConcurrentParseParameter] = [
    ConcurrentParseParameter(scenarios=("parse_query",)),
    ConcurrentParseParameter(scenarios=("ParsedSPARQL",)),
    ConcurrentParseParameter(scenarios=("get_query_projection",)),
    ConcurrentParseParameter(scenarios=("get_page",)),
    ConcurrentParseParameter(scenarios=("get_item",)),
    ConcurrentParseParameter(scenarios=("get_page", "get_item")),
]


@pytest.mark.parametrize("param", params)
def test_concurrent_cold_parse(param):
    result: subprocess.CompletedProcess = subprocess.run(
        [sys.executable, "-c", script, str(param.threads), *param.scenarios],
        capture_output=True,
        text=True,
        check=True,
        timeout=60,
    )
    failures: list[str] = json.loads(result.stdout)

    assert failures == []
