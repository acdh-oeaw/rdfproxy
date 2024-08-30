from tests.data.models.author_array_collection_model import Author
from tests.utils._types import Parameter


author_array_collection_parameters = [
    Parameter(
        model=Author,
        bindings=[
            {
                "work": "http://www.wikidata.org/entity/Q1497409",
                "gnd": "119359464",
                "work_name": "Geb\u00fcrtig",
                "nameLabel": "Schindel",
            },
            {
                "work": "http://www.wikidata.org/entity/Q15805238",
                "gnd": "115612815",
                "work_name": "Der alte K\u00f6nig in seinem Exil",
                "nameLabel": "Geiger",
                "viaf": "299260555",
                "educated_atLabel": "University of Vienna",
            },
            {
                "work": "http://www.wikidata.org/entity/Q15805238",
                "gnd": "115612815",
                "work_name": "Der alte K\u00f6nig in seinem Exil",
                "nameLabel": "Geiger",
                "viaf": "6762154387354230970008",
                "educated_atLabel": "University of Vienna",
            },
            {
                "work": "http://www.wikidata.org/entity/Q58038819",
                "gnd": "115612815",
                "work_name": "Unter der Drachenwand",
                "nameLabel": "Geiger",
                "viaf": "2277151717053313900002",
                "educated_atLabel": "University of Vienna",
            },
            {
                "work": "http://www.wikidata.org/entity/Q100266054",
                "gnd": "1136992030",
                "work_name": "Das fl\u00fcssige Land",
                "nameLabel": "Edelbauer",
                "educated_atLabel": "University of Vienna",
            },
            {
                "work": "http://www.wikidata.org/entity/Q100266054",
                "gnd": "1136992030",
                "work_name": "Das fl\u00fcssige Land",
                "nameLabel": "Edelbauer",
                "educated_atLabel": "University of Applied Arts Vienna",
            },
        ],
        expected=[
            {
                "gnd": "119359464",
                "surname": "Schindel",
                "works": [{"name": "Geb\u00fcrtig", "viafs": []}],
                "education": [],
            },
            {
                "gnd": "115612815",
                "surname": "Geiger",
                "works": [
                    {
                        "name": "Der alte K\u00f6nig in seinem Exil",
                        "viafs": ["299260555", "6762154387354230970008"],
                    },
                    {
                        "name": "Unter der Drachenwand",
                        "viafs": ["2277151717053313900002"],
                    },
                ],
                "education": ["University of Vienna"],
            },
            {
                "gnd": "1136992030",
                "surname": "Edelbauer",
                "works": [{"name": "Das fl\u00fcssige Land", "viafs": []}],
                "education": [
                    "University of Vienna",
                    "University of Applied Arts Vienna",
                ],
            },
        ],
    )
]
