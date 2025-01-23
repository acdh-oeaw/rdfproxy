"""Custom exceptions for RDFProxy."""


class MissingModelConfigException(Exception):
    """Exception for indicating that an expected Config class is missing in a Pydantic model definition."""


class InvalidGroupingKeyException(Exception):
    """Exception for indicating that an invalid grouping key has been encountered."""


class QueryConstructionException(Exception):
    """Exception for indicating failed SPARQL query construction."""


class UnsupportedQueryException(Exception):
    """Exception for indicating that a given SPARQL query is not supported."""


class QueryParseException(Exception):
    """Exception for indicating that a given SPARQL query raised a parse error.

    This exception is intended to wrap and re-raise all exceptions
    raised from parsing a SPARQL query with RDFLib's parseQuery function.

    parseQuery raises a pyparsing.exceptions.ParseException,
    which would require to introduce pyparsing as a dependency just for testing.
    """
