"""Custom exceptions for RDFProxy."""


class RDFProxyBaseException(Exception):
    """Base Exception class for RDFProxy exceptions."""


class MissingModelConfigException(RDFProxyBaseException):
    """Exception for indicating that an expected Config class is missing in a Pydantic model definition."""


class InvalidGroupingKeyException(RDFProxyBaseException):
    """Exception for indicating that an invalid grouping key has been encountered."""


class QueryConstructionException(RDFProxyBaseException):
    """Exception for indicating failed SPARQL query construction."""


class UnsupportedQueryException(RDFProxyBaseException):
    """Exception for indicating that a given SPARQL query is not supported."""


class QueryParseException(RDFProxyBaseException):
    """Exception for indicating that a given SPARQL query raised a parse error.

    This exception is intended to wrap and re-raise all exceptions
    raised from parsing a SPARQL query with RDFLib's parseQuery function.

    parseQuery raises a pyparsing.exceptions.ParseException,
    which would require to introduce pyparsing as a dependency just for testing.
    """


class ModelValidationException(RDFProxyBaseException):
    """Exception for indicating that a model is invalid according to RDFProxy semantics"""


class GroupByException(ModelValidationException):
    """Exception for indicating invalid group_by definitions."""


class ModelBoolException(ModelValidationException):
    """Exception for indicating invalid model_bool definitions."""


class ModelFieldException(ModelValidationException):
    """Exception for indicating invalid model field definitions."""
