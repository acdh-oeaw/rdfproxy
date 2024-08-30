"""Custom exceptions for RDFProxy."""


class UndefinedBindingException(KeyError):
    """Exception for indicating that a requested key could not be retrieved from a SPARQL binding mapping."""


class InterdependentParametersException(Exception):
    """Exceptiono for indicating that two or more parameters are interdependent."""


class MissingModelConfigException(Exception):
    """Exception for indicating that an expected Config class is missing in a Pydantic model definition."""


class UnboundGroupingKeyException(Exception):
    """Exception for indicating that no SPARQL binding corresponds to the requested grouping key."""
