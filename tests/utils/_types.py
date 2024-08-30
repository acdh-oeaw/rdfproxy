"""Types for testing."""

from collections import namedtuple


Parameter = namedtuple("Parameter", ["model", "bindings", "expected"])
