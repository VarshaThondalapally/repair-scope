from pathlib import Path
import hashlib
import json
import os
import pytest
from fastapi.testclient import TestClient
from finding_coder.server import app
from finding_coder.catalog import parse_catalog
from finding_coder.matcher import Matcher,Synonyms
from finding_coder.export import safe_cell
from finding_coder.domains import load_domain
from finding_coder.review import triage
from fastapi import HTTPException
from finding_coder.server import Query, export as export_route
from finding_coder.catalog import CatalogError
from pydantic import ValidationError


def test_export_route_enforces_explicit_approval():
    q={"domain":"rv_service","finding":"Replace failed roof vent lid","codes":["RVS-0904"]}
    with pytest.raises(HTTPException) as error:
        export_route(Query(**q))
    assert error.value.status_code==409
    response=export_route(Query(**q,review_confirmed=True,reviewer="Varsha"))
    assert response.status_code==200 and b"RVS-0904" in response.body


def test_export_route_refuses_undocumented_override():
    q={"domain":"rv_service","finding":"Replace regulator","codes":["RVS-0202"],"review_confirmed":True,"reviewer":"Varsha","allow_incomplete":True}
    with pytest.raises(HTTPException):
        export_route(Query(**q))
    assert export_route(Query(**q,override_reason="Example rule reviewed, intentionally incomplete draft")).status_code==200


def test_request_limit_is_enforced():
    with pytest.raises(ValidationError):
        Query(finding="x"*2001)


def test_multiline_catalog_and_duplicate_headers():
    catalog=parse_catalog('\ufeffcode,section,description,hours\nA,S,"One,\n two",1.5\n')
    assert catalog.get("A").description=="One,\n two"
    with pytest.raises(CatalogError):
        parse_catalog("code,section,description,hours,hours\nA,S,D,1,2")


def test_generic_direction_words_are_not_repair_evidence():
    assert not load_domain("rv_service").matcher.rank("up front off")


def test_phrase_alias_does_not_match_one_word_only():
    catalog=parse_catalog("code,section,description,hours\nA,S,Set air mover,1\nB,S,Replace air filter,1\n")
    assert [c.row.code for c in Matcher(catalog,Synonyms([["blower","air mover"]])).rank("blower")]==["A"]


def test_multiple_alias_words_are_one_source():
    catalog=parse_catalog("code,section,description,hours\nA,S,Set air mover,1\n")
    assert not Matcher(catalog,Synonyms([["blower","air mover"]])).match("blower").confident


def test_typos_are_visible_and_not_confidence_evidence():
    catalog=parse_catalog("code,section,description,hours\nA,S,Replace furnace igniter,1\n")
    result=Matcher(catalog).match("furnase")
    assert result.candidates[0].matched[0].via_typo
    assert not result.confident


def test_batch_never_exports_without_review():
    coded,queue=triage(load_domain("rv_service"),["Replace failed roof vent lid"])
    assert not coded and len(queue)==1 and "Human approval" in queue[0].why


@pytest.mark.parametrize("value",["=1","+cmd","-cmd","@SUM(A1)","  =1","\tX","\rX"])
def test_formula_injection(value):
    assert safe_cell(value).startswith("'")


def test_frozen_baseline_unchanged():
    root=Path(__file__).resolve().parents[1]/"benchmarks"
    for relative,digest in json.loads((root/"manifest.json").read_text()).items():
        assert hashlib.sha256((root/relative).read_bytes()).hexdigest()==digest, relative


@pytest.mark.skipif(os.environ.get("RUN_HTTP_TESTS") != "1", reason="HTTP integration requires a runtime with local sockets; enabled in CI")
def test_http_review_gate_static_assets_and_limits():
    with TestClient(app) as c:
        assert c.get("/").status_code==200
        assert c.get("/engine.js").status_code==200
        assert c.get("/").headers["X-Content-Type-Options"]=="nosniff"
        q={"domain":"rv_service","finding":"Replace failed roof vent lid","codes":["RVS-0904"]}
        assert c.post("/api/export",json=q).status_code==409
        q.update(review_confirmed=True,reviewer="Varsha")
        response=c.post("/api/export",json=q)
        assert response.status_code==200 and "RVS-0904" in response.text
        assert c.post("/api/match",json={"domain":"../../","finding":"x"}).status_code==400
        assert c.post("/api/match",json={"domain":"rv_service","finding":"x"*2001}).status_code==422


@pytest.mark.skipif(os.environ.get("RUN_HTTP_TESTS") != "1", reason="HTTP integration requires a runtime with local sockets; enabled in CI")
def test_http_override_requires_reason():
    with TestClient(app) as c:
        q={"domain":"rv_service","finding":"Replace LP regulator","codes":["RVS-0202"],"review_confirmed":True,"reviewer":"Varsha","allow_incomplete":True}
        assert c.post("/api/export",json=q).status_code==409
        q["override_reason"]="Example rule reviewed; draft intentionally incomplete"
        assert c.post("/api/export",json=q).status_code==200
