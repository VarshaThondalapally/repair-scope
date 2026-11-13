"""An uploaded catalog with no rules file, the web-facing views, and the bundled packs."""

import pytest

from finding_coder import api
from finding_coder.catalog import CatalogError
from finding_coder.domains import list_domains, load_domain, pack_from_catalog_text
from finding_coder.evaluate import evaluate, load_gold

UPLOAD = """code,section,description,hours
LIFT-01,Hydraulics,Replace hydraulic hose,0.8
LIFT-02,Hydraulics,Replace lift cylinder seal kit,2.0
LIFT-03,Electrical,Replace battery charger,0.6
"""


def test_uploaded_catalog_without_rules_still_matches():
    pack = pack_from_catalog_text(UPLOAD)
    assert pack.rules == () and not pack.has_rules_file
    result = api.run_match(pack, "hydraulic hoses leaking at the fitting")
    assert result["candidates"][0]["code"] == "LIFT-01"
    assert result["confident"]


def test_uploaded_catalog_without_rules_still_validates_codes_exactly():
    pack = pack_from_catalog_text(UPLOAD)
    checked = api.run_check(pack, "hydraulic hoses leaking", ["LIFT-01", "LIFT-1"])
    assert [line["status"] for line in checked["lines"]] == ["passed", "blocked: not in catalog"]
    assert checked["missing"] == [] and checked["complete"]
    assert checked["has_rules_file"] is False and checked["rules"] == 0


def test_uploaded_catalog_export_leaves_out_blocked_lines():
    pack = pack_from_catalog_text(UPLOAD)
    text = api.run_export(pack, "hydraulic hoses leaking", ["LIFT-01", "LIFT-1"], False)
    assert text.splitlines()[1:] == [
        "hydraulic hoses leaking,LIFT-01,Hydraulics,Replace hydraulic hose,0.8,passed"
    ]


def test_bad_upload_is_rejected_with_problems():
    with pytest.raises(CatalogError) as error:
        pack_from_catalog_text("code,section,description,hours\nA,S,D,x\n")
    assert error.value.problems


def test_highlight_marks_matched_words_only():
    assert api.highlight("Replace hydraulic hoses", {"hose"}) == [
        ["Replace", False],
        [" ", False],
        ["hydraulic", False],
        [" ", False],
        ["hoses", True],
    ]


def test_bundled_domains_load_and_fit_the_spec():
    assert list_domains() == ["property_restoration", "rv_service"]
    for name in list_domains():
        pack = load_domain(name)
        assert 40 <= len(pack.catalog) <= 70
        assert pack.has_rules_file and pack.rules
        gold = load_gold(pack.folder / "gold.csv")
        assert 30 <= len(gold) <= 40
        scores = evaluate(pack, gold)  # raises if gold uses a code the catalog lacks
        assert scores.total == len(gold)


def test_domain_can_be_loaded_from_a_folder_without_rules(tmp_path):
    (tmp_path / "catalog.csv").write_text(UPLOAD, encoding="utf-8")
    pack = load_domain(str(tmp_path))
    assert len(pack.catalog) == 3 and not pack.has_rules_file


def test_unknown_domain_is_a_clear_error():
    with pytest.raises(FileNotFoundError, match="Bundled domains"):
        load_domain("no_such_domain")
