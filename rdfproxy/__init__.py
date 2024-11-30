from beartype.claw import beartype_this_package

beartype_this_package()

from rdfproxy.adapter import SPARQLModelAdapter  # noqa: F401, E402
from rdfproxy.mapper import ModelBindingsMapper  # noqa: F401, E402
from rdfproxy.utils._types import SPARQLBinding  # noqa: F401, E402
from rdfproxy.utils.models import Page  # noqa: F401, E402
