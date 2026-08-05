import json


class StructuredMessage:
    """Structured log message class.

    This is taken from the Python logging cookbook:
    https://docs.python.org/3/howto/logging-cookbook.html#implementing-structured-logging;
    jsond.dumps.default is set to str for logging of non-json-serializable objects.
    """

    def __init__(self, message: str, **kwargs) -> None:
        self.message = message
        self.kwargs = kwargs

    def __str__(self) -> str:
        return "%s >>> %s" % (self.message, json.dumps(self.kwargs, default=str))
