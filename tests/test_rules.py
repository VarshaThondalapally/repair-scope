import pytest

from finding_coder.rules import (
    RulesError,
    check_rules_fit_catalog,
    find_missing,
    load_rules,
    parse_rules,
)


def one_rule(when, require):
    return parse_rules(
        {"rules": [{"name": "r", "reason": "because", "when": when, "require": require}]}
    )


def rows(catalog, *codes):
    return [catalog.get(code) for code in codes]


def test_section_only_trigger(catalog):
    rules = one_rule({"section": "roof"}, {"code": "D-1"})
    assert len(find_missing(rules, rows(catalog, "R-1"), catalog)) == 1
    assert find_missing(rules, rows(catalog, "W-1"), catalog) == []


def test_section_list_trigger(catalog):
    rules = one_rule({"section": ["Roof", "Gas"]}, {"code": "D-1"})
    assert len(find_missing(rules, rows(catalog, "G-1"), catalog)) == 1
    assert find_missing(rules, rows(catalog, "W-1"), catalog) == []


def test_description_trigger_matches_whole_phrase_only(catalog):
    rules = one_rule({"description_any": ["water pump"]}, {"code": "W-3"})
    assert len(find_missing(rules, rows(catalog, "W-1"), catalog)) == 1
    # "Replace water heater igniter" has "water" but not the phrase "water pump".
    assert find_missing(rules, rows(catalog, "W-2"), catalog) == []


def test_description_trigger_ignores_plural_and_case(catalog):
    rules = one_rule({"description_any": ["VENTS"]}, {"code": "D-1"})
    assert len(find_missing(rules, rows(catalog, "R-1"), catalog)) == 1


def test_section_and_description_must_both_hold(catalog):
    rules = one_rule({"section": "Gas", "description_any": ["replace"]}, {"code": "G-2"})
    assert len(find_missing(rules, rows(catalog, "G-1"), catalog)) == 1
    assert find_missing(rules, rows(catalog, "W-1"), catalog) == []  # replace, wrong section
    assert find_missing(rules, rows(catalog, "G-2"), catalog) == []  # right section, no replace


def test_description_none_excludes_rows(catalog):
    rules = one_rule(
        {"section": "Roof", "description_any": ["vent"], "description_none": ["lid"]},
        {"code": "D-1"},
    )
    assert len(find_missing(rules, rows(catalog, "R-1"), catalog)) == 1
    assert find_missing(rules, rows(catalog, "R-2"), catalog) == []


def test_code_trigger(catalog):
    rules = one_rule({"code": ["R-1", "R-2"]}, {"code": "D-1"})
    assert len(find_missing(rules, rows(catalog, "R-2"), catalog)) == 1
    assert find_missing(rules, rows(catalog, "G-1"), catalog) == []


def test_require_by_code_reports_the_satisfying_row(catalog, rules):
    (gap,) = find_missing(rules, rows(catalog, "G-1"), catalog)
    assert gap.rule.name == "Gas work needs a leak test"
    assert [row.code for row in gap.triggered_by] == ["G-1"]
    assert [row.code for row in gap.satisfied_by] == ["G-2"]


def test_require_by_pattern_reports_the_satisfying_row(catalog, rules):
    (gap,) = find_missing(rules, rows(catalog, "W-1"), catalog)
    assert [row.code for row in gap.satisfied_by] == ["W-3"]


def test_rule_is_satisfied_when_companion_is_present(catalog, rules):
    assert find_missing(rules, rows(catalog, "G-1", "G-2"), catalog) == []
    assert find_missing(rules, rows(catalog, "W-1", "W-3"), catalog) == []


def test_nothing_triggers_on_unrelated_lines(catalog, rules):
    assert find_missing(rules, rows(catalog, "R-1", "D-1"), catalog) == []


@pytest.mark.parametrize(
    "document",
    [
        {},
        {"rules": "nope"},
        {"rules": [{"name": "r", "reason": "x", "when": {"section": "Gas"}}]},
        {"rules": [{"name": "r", "reason": "x", "when": {}, "require": {"code": "G-2"}}]},
        {"rules": [{"name": "r", "reason": "x", "when": {"sect": "Gas"}, "require": {"code": "G-2"}}]},
        {"rules": [{"name": "r", "reason": "x", "when": {"section": []}, "require": {"code": "G-2"}}]},
    ],
)
def test_malformed_rules_are_rejected(document):
    with pytest.raises(RulesError):
        parse_rules(document)


def test_rule_pointing_at_a_code_the_catalog_lacks_is_rejected(catalog):
    rules = one_rule({"section": "Gas"}, {"code": "G-99"})
    with pytest.raises(RulesError, match="no catalog row matches 'require'"):
        check_rules_fit_catalog(rules, catalog)


def test_rule_that_can_never_fire_is_rejected(catalog):
    rules = one_rule({"section": "Brakes"}, {"code": "G-2"})
    with pytest.raises(RulesError, match="no catalog row matches 'when'"):
        check_rules_fit_catalog(rules, catalog)


def test_load_rules_from_yaml_file(tmp_path, catalog):
    path = tmp_path / "rules.yaml"
    path.write_text(
        "rules:\n"
        "  - name: Gas work needs a leak test\n"
        "    reason: Opened gas lines are leak tested.\n"
        "    when: {section: Gas, description_any: [replace]}\n"
        "    require: {code: G-2}\n",
        encoding="utf-8",
    )
    rules = load_rules(path)
    check_rules_fit_catalog(rules, catalog)
    assert len(find_missing(rules, rows(catalog, "G-1"), catalog)) == 1
