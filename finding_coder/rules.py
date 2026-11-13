"""Completeness rules: "when a line like A is selected, a line like B must be there too".

Rules are data (one YAML file per domain), written by someone who knows the
trade. This module only loads them and evaluates them against selected lines.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from .catalog import Catalog, CatalogRow
from .matcher import contains_phrase, tokenize

CONDITION_KEYS = {"code", "section", "description_any", "description_none"}


class RulesError(ValueError):
    """Raised when a rules file is malformed or does not fit its catalog."""


@dataclass(frozen=True)
class Condition:
    """Describes a kind of catalog row. Every field that is set must hold.

    codes            -- the row's code is one of these (exact)
    sections         -- the row's section is one of these (case-insensitive)
    description_any  -- the description contains at least one of these phrases
    description_none -- the description contains none of these phrases
    Phrases are compared after the same word normalisation the matcher uses.
    """

    codes: tuple[str, ...] = ()
    sections: tuple[str, ...] = ()
    description_any: tuple[tuple[str, ...], ...] = ()
    description_none: tuple[tuple[str, ...], ...] = ()

    def matches(self, row: CatalogRow) -> bool:
        if self.codes and row.code not in self.codes:
            return False
        if self.sections and row.section.lower() not in self.sections:
            return False
        tokens = tokenize(row.description)
        if self.description_any and not any(
            contains_phrase(tokens, phrase) for phrase in self.description_any
        ):
            return False
        return not any(contains_phrase(tokens, phrase) for phrase in self.description_none)


@dataclass(frozen=True)
class Rule:
    """A named completeness rule with a plain-language reason."""

    name: str
    reason: str
    when: Condition
    require: Condition


@dataclass(frozen=True)
class Missing:
    """A rule that fired but was not satisfied by the selected lines."""

    rule: Rule
    triggered_by: tuple[CatalogRow, ...]
    satisfied_by: tuple[CatalogRow, ...]  # catalog rows that would satisfy the rule


def _as_list(value, where: str) -> list[str]:
    values = [value] if isinstance(value, str) else value
    if not isinstance(values, list) or not values or not all(
        isinstance(item, str) and item.strip() for item in values
    ):
        raise RulesError(f"{where}: expected a word or a list of words")
    return [item.strip() for item in values]


def _parse_condition(data, where: str) -> Condition:
    if not isinstance(data, dict) or not data:
        raise RulesError(f"{where}: must set at least one of {sorted(CONDITION_KEYS)}")
    unknown = set(data) - CONDITION_KEYS
    if unknown:
        raise RulesError(f"{where}: unknown key(s) {sorted(unknown)}")
    lists = {key: _as_list(value, f"{where}.{key}") for key, value in data.items()}
    return Condition(
        codes=tuple(lists.get("code", ())),
        sections=tuple(section.lower() for section in lists.get("section", ())),
        description_any=tuple(tuple(tokenize(p)) for p in lists.get("description_any", ())),
        description_none=tuple(tuple(tokenize(p)) for p in lists.get("description_none", ())),
    )


def parse_rules(data) -> list[Rule]:
    """Build rules from the parsed YAML document `{rules: [...]}`."""
    entries = data.get("rules") if isinstance(data, dict) else None
    if not isinstance(entries, list):
        raise RulesError("rules file must contain a top-level 'rules:' list")
    rules = []
    for index, entry in enumerate(entries, start=1):
        where = f"rule {index}"
        if not isinstance(entry, dict):
            raise RulesError(f"{where}: must be a mapping")
        for key in ("name", "reason", "when", "require"):
            if not entry.get(key):
                raise RulesError(f"{where}: missing '{key}'")
        where = f"rule {index} ({entry['name']})"
        rules.append(
            Rule(
                name=str(entry["name"]),
                reason=str(entry["reason"]),
                when=_parse_condition(entry["when"], f"{where}.when"),
                require=_parse_condition(entry["require"], f"{where}.require"),
            )
        )
    return rules


def load_rules(path: str | Path) -> list[Rule]:
    """Load completeness rules from a YAML file."""
    return parse_rules(yaml.safe_load(Path(path).read_text(encoding="utf-8")))


def check_rules_fit_catalog(rules: list[Rule], catalog: Catalog) -> None:
    """Fail loudly if a rule can never fire or can never be satisfied in this catalog."""
    problems = []
    for rule in rules:
        if not any(rule.when.matches(row) for row in catalog.rows):
            problems.append(f"rule '{rule.name}': no catalog row matches 'when'")
        if not any(rule.require.matches(row) for row in catalog.rows):
            problems.append(f"rule '{rule.name}': no catalog row matches 'require'")
    if problems:
        raise RulesError("Rules do not fit the catalog:\n- " + "\n- ".join(problems))


def find_missing(
    rules: list[Rule], selected: list[CatalogRow], catalog: Catalog
) -> list[Missing]:
    """Return every rule triggered by `selected` whose required line is absent.

    Only one step is evaluated: if adding a required line triggers a further
    rule, that shows up the next time the (larger) set is checked.
    """
    missing = []
    for rule in rules:
        triggers = tuple(row for row in selected if rule.when.matches(row))
        if triggers and not any(rule.require.matches(row) for row in selected):
            satisfied_by = tuple(row for row in catalog.rows if rule.require.matches(row))
            missing.append(Missing(rule, triggers, satisfied_by))
    return missing
