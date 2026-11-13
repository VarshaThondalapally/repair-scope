import csv
import io

import pytest

from finding_coder.checker import ProposedLine, check
from finding_coder.domains import DomainPack
from finding_coder.export import FIELDS, ExportError, approved_lines, to_csv, write_csv
from finding_coder.review import triage, write_queue

FINDING = "gas regulator hissing at the bottles"


def report_for(catalog, matcher, rules, finding, *codes):
    return check(finding, [ProposedLine(code) for code in codes], catalog, matcher, rules)


def test_export_writes_passed_lines(tmp_path, catalog, matcher, rules):
    report = report_for(catalog, matcher, rules, FINDING, "G-1", "G-2")
    path = tmp_path / "out.csv"
    write_csv(path, approved_lines(report))
    with open(path, newline="", encoding="utf-8") as handle:
        records = list(csv.DictReader(handle))
    assert tuple(records[0]) == FIELDS
    assert [record["code"] for record in records] == ["G-1", "G-2"]
    assert records[0]["finding"] == FINDING
    assert records[0]["hours"] == "0.5"
    assert records[1]["description"] == "Gas leak test"


def test_export_refuses_an_incomplete_set_unless_told(catalog, matcher, rules):
    report = report_for(catalog, matcher, rules, FINDING, "G-1")
    with pytest.raises(ExportError, match="Gas work needs a leak test"):
        approved_lines(report)
    lines = approved_lines(report, allow_incomplete=True)
    assert [(line.row.code, line.note) for line in lines] == [("G-1", "incomplete")]


def test_export_never_includes_blocked_lines(catalog, matcher, rules):
    report = report_for(catalog, matcher, rules, FINDING, "G-1", "G-2", "NOPE-1")
    assert [line.row.code for line in approved_lines(report)] == ["G-1", "G-2"]


def test_needs_person_lines_are_exported_only_after_review(catalog, matcher, rules):
    report = report_for(catalog, matcher, rules, FINDING, "G-1", "G-2", "R-1")
    assert [line.row.code for line in approved_lines(report)] == ["G-1", "G-2"]
    reviewed = approved_lines(report, reviewed={"R-1"})
    assert [(line.row.code, line.note) for line in reviewed][-1] == ("R-1", "reviewed by a person")


def test_csv_quotes_commas(catalog, matcher, rules):
    report = report_for(catalog, matcher, rules, "gas regulator, hissing", "G-1", "G-2")
    rows = list(csv.reader(io.StringIO(to_csv(approved_lines(report)))))
    assert rows[1][0] == "gas regulator, hissing"


def test_triage_requires_review_for_every_finding(
    tmp_path, catalog, matcher, rules
):
    pack = DomainPack("test", catalog, matcher, tuple(rules), True)
    coded, queue = triage(pack, [FINDING, "roof vent", "something smells odd"])
    assert coded == []
    assert [item.finding for item in queue] == [FINDING, "roof vent", "something smells odd"]
    assert all("Human approval required" in item.why for item in queue)

    path = tmp_path / "queue.csv"
    write_queue(path, queue)
    with open(path, newline="", encoding="utf-8") as handle:
        records = list(csv.DictReader(handle))
    assert records[0]["candidate_1"].startswith("G-")
    assert records[1]["candidate_1"].startswith("R-")
    assert records[2]["candidate_1"] == ""
