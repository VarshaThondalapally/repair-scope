from finding_coder.checker import ProposedLine, Status, check

FINDING = "gas regulator hissing at the bottles"


def run(catalog, matcher, rules, finding, *lines, sections=None):
    proposed = [line if isinstance(line, ProposedLine) else ProposedLine(line) for line in lines]
    return check(finding, proposed, catalog, matcher, rules, sections)


def test_passed_when_valid_supported_and_complete(catalog, matcher, rules):
    report = run(catalog, matcher, rules, FINDING, "G-1", "G-2")
    assert [line.status for line in report.lines] == [Status.PASSED, Status.PASSED]
    assert report.complete and not report.has_blocked
    assert report.lines[1].reason == "Required by rule 'Gas work needs a leak test'."


def test_valid_but_incomplete(catalog, matcher, rules):
    """Every code exists and fits the finding, yet the set is not complete."""
    report = run(catalog, matcher, rules, FINDING, "G-1")
    (line,) = report.lines
    assert line.status is Status.INCOMPLETE
    assert "G-2" in line.reason
    assert not report.complete and not report.has_blocked
    assert [row.code for row in report.missing[0].satisfied_by] == ["G-2"]


def test_blocked_when_code_is_not_in_catalog(catalog, matcher, rules):
    report = run(catalog, matcher, rules, FINDING, "G-11")
    (line,) = report.lines
    assert line.status is Status.NOT_IN_CATALOG and line.status.blocked
    assert line.row is None
    assert "Closest existing code is G-1" in line.reason


def test_near_miss_codes_are_not_silently_accepted(catalog, matcher, rules):
    for code in ("g-1", "G-1 ", "G1"):
        assert run(catalog, matcher, rules, FINDING, code).lines[0].status is Status.NOT_IN_CATALOG


def test_blocked_when_claimed_section_disagrees_with_catalog(catalog, matcher, rules):
    report = run(catalog, matcher, rules, FINDING, ProposedLine("G-1", section="Water"))
    assert report.lines[0].status is Status.WRONG_SECTION
    assert "under 'Gas', not 'Water'" in report.lines[0].reason
    assert run(catalog, matcher, rules, FINDING, ProposedLine("G-1", "gas"), "G-2").lines[
        0
    ].status is Status.PASSED


def test_blocked_when_code_is_outside_the_sections_given_for_the_finding(catalog, matcher, rules):
    report = run(catalog, matcher, rules, FINDING, "G-1", "G-2", "R-1", sections=["Gas"])
    assert [line.status for line in report.lines] == [
        Status.PASSED,
        Status.PASSED,
        Status.WRONG_SECTION,
    ]


def test_blocked_lines_do_not_trigger_or_satisfy_rules(catalog, matcher, rules):
    report = run(catalog, matcher, rules, FINDING, "G-1", "G-2", sections=["Water"])
    assert report.has_blocked and report.missing == ()


def test_needs_person_when_no_word_supports_the_line(catalog, matcher, rules):
    report = run(catalog, matcher, rules, FINDING, "R-1")
    assert report.lines[0].status is Status.NEEDS_PERSON
    assert report.lines[0].reason == "No word of the finding points at R-1."


def test_needs_person_when_an_unselected_row_is_as_good(catalog, matcher, rules):
    report = run(catalog, matcher, rules, "roof vent", "R-1")
    assert report.lines[0].status is Status.NEEDS_PERSON
    assert "Too close to call" in report.lines[0].reason


def test_needs_person_when_an_unselected_row_fits_better(catalog, matcher, rules):
    report = run(catalog, matcher, rules, "roof vent lid cracked", "R-1")
    assert report.lines[0].status is Status.NEEDS_PERSON
    assert "Another row fits the wording better: R-2" in report.lines[0].reason


def test_empty_finding_skips_the_wording_check(catalog, matcher, rules):
    report = run(catalog, matcher, rules, "", "R-1")
    assert report.lines[0].status is Status.PASSED


def test_every_line_has_a_one_sentence_reason(catalog, matcher, rules):
    report = run(catalog, matcher, rules, FINDING, "G-1", "R-1", "ZZ-9", ProposedLine("W-1", "Roof"))
    assert {line.status for line in report.lines} == {
        Status.INCOMPLETE,
        Status.NEEDS_PERSON,
        Status.NOT_IN_CATALOG,
        Status.WRONG_SECTION,
    }
    assert all(line.reason.strip().endswith(".") for line in report.lines)
