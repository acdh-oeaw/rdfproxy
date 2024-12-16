"""Testing utils."""

import re


def normalize_query(select_query: str) -> str:
    """Normalize whitespace chars in a SPARQL query."""
    normalized_select_query = re.sub(
        r"(?<!\w)([{}.,;()?])(?!\w)", r" \1 ", select_query
    )
    return " ".join(normalized_select_query.split())
