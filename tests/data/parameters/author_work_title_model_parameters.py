from tests.data.models.author_work_title_model import Author
from tests.utils._types import Parameter


author_work_title_parameters = [
    Parameter(
        model=Author,
        bindings=[
            {"author": "Author 1", "work": "Work 1", "year": 2000},
            {"author": "Author 2", "work": "Work 4", "year": 2000},
            {"author": "Author 1", "work": "Work 2", "year": 2000},
            {"author": "Author 1", "work": "Work 3", "year": 2001},
        ],
        expected=[
            {
                "name": "Author 1",
                "works": [
                    {"year": 2000, "titles": [{"name": "Work 1"}, {"name": "Work 2"}]},
                    {"year": 2001, "titles": [{"name": "Work 3"}]},
                ],
            },
            {
                "name": "Author 2",
                "works": [{"year": 2000, "titles": [{"name": "Work 4"}]}],
            },
        ],
    )
]
