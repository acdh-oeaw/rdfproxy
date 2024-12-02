"""Custom exceptions for RDFProxy."""


class MissingModelConfigException(Exception):
    """Exception for indicating that an expected Config class is missing in a Pydantic model definition."""


class InvalidGroupingKeyException(Exception):
    """Exception for indicating that an invalid grouping key has been encountered."""


class QueryConstructionException(Exception):
    """Exception for indicating failed SPARQL query construction."""
