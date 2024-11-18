"""Custom exceptions for RDFProxy."""


class MissingModelConfigException(Exception):
    """Exception for indicating that an expected Config class is missing in a Pydantic model definition."""


class UnboundGroupingKeyException(Exception):
    """Exception for indicating that no SPARQL binding corresponds to the requested grouping key."""


class UnsupportedQueryException(Exception):
    """Exception for indicating that a given SPARQL query is not supported."""
