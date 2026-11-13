"""Shared fixtures: a tiny hand-made catalog so tests do not depend on the domain packs."""

import pytest

from finding_coder.catalog import parse_catalog
from finding_coder.matcher import Matcher, Synonyms
from finding_coder.rules import parse_rules

CATALOG_CSV = """code,section,description,hours
G-1,Gas,Replace gas regulator,0.5
G-2,Gas,Gas leak test,0.4
W-1,Water,Replace water pump,0.7
W-2,Water,Replace water heater igniter,0.5
W-3,Water,Pressure test water lines,0.4
R-1,Roof,Reseal roof vent,0.8
R-2,Roof,Replace roof vent lid,0.4
D-1,Diagnosis,Diagnose appliance fault,0.5
"""

RULES = {
    "rules": [
        {
            "name": "Gas work needs a leak test",
            "reason": "Opened gas lines are leak tested.",
            "when": {"section": "Gas", "description_any": ["replace"]},
            "require": {"code": "G-2"},
        },
        {
            "name": "Pump needs a pressure test",
            "reason": "Opened water lines are pressure tested.",
            "when": {"description_any": ["water pump"]},
            "require": {"section": "Water", "description_any": ["pressure test"]},
        },
    ]
}


@pytest.fixture
def catalog():
    return parse_catalog(CATALOG_CSV)


@pytest.fixture
def matcher(catalog):
    return Matcher(catalog, Synonyms([["propane", "lp", "gas"], ["won't light", "igniter"]]))


@pytest.fixture
def rules():
    return parse_rules(RULES)
