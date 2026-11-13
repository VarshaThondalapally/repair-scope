"""Check a set of proposed codes for one finding and give each line a status.

The proposed codes can come from the matcher, from a person, or from any
outside system. Nothing is trusted: every code is looked up exactly.
"""

from __future__ import annotations

import difflib
from dataclasses import dataclass
from enum import Enum

from .catalog import Catalog, CatalogRow
from .matcher import Matcher, judge
from .rules import Missing, Rule, find_missing


class Status(str, Enum):
    PASSED = "passed"
    NOT_IN_CATALOG = "blocked: not in catalog"
    WRONG_SECTION = "blocked: wrong section"
    NEEDS_PERSON = "needs a person"
    INCOMPLETE = "incomplete"

    @property
    def blocked(self) -> bool:
        return self in (Status.NOT_IN_CATALOG, Status.WRONG_SECTION)


@dataclass(frozen=True)
class ProposedLine:
    """A code someone wants to use, optionally with the section they believe it is in."""

    code: str
    section: str | None = None


@dataclass(frozen=True)
class LineResult:
    code: str
    status: Status
    reason: str
    row: CatalogRow | None  # None when the code is not in the catalog


@dataclass(frozen=True)
class CheckReport:
    finding: str
    lines: tuple[LineResult, ...]
    missing: tuple[Missing, ...]

    @property
    def complete(self) -> bool:
        return not self.missing

    @property
    def has_blocked(self) -> bool:
        return any(line.status.blocked for line in self.lines)


def _blocked(line: ProposedLine, catalog: Catalog, allowed: set[str]) -> LineResult | None:
    """Return a blocked result if the line fails an exact catalog check, else None."""
    row = catalog.get(line.code)
    if row is None:
        near = difflib.get_close_matches(line.code, catalog.codes(), n=1, cutoff=0.8)
        hint = f" Closest existing code is {near[0]}." if near else ""
        return LineResult(
            line.code,
            Status.NOT_IN_CATALOG,
            f"Code {line.code!r} does not exist in the catalog.{hint}",
            None,
        )
    if line.section is not None and line.section.strip().lower() != row.section.lower():
        return LineResult(
            line.code,
            Status.WRONG_SECTION,
            f"The catalog files {line.code} under '{row.section}', not '{line.section}'.",
            row,
        )
    if allowed and row.section.lower() not in allowed:
        return LineResult(
            line.code,
            Status.WRONG_SECTION,
            f"{line.code} is in '{row.section}', which is not a section given for this finding.",
            row,
        )
    return None


def check(
    finding: str,
    proposed: list[ProposedLine],
    catalog: Catalog,
    matcher: Matcher,
    rules: list[Rule] | tuple[Rule, ...] = (),
    finding_sections: list[str] | None = None,
) -> CheckReport:
    """Give every proposed line one status and a one-sentence reason.

    Order of checks per line: exact catalog lookup, section, wording support
    (the matcher's confident rule, against rows that were NOT proposed), then
    completeness rules. A line required by a rule that another line triggered
    passes without wording support, since nobody writes "leak test" in a finding.
    """
    allowed = {section.strip().lower() for section in (finding_sections or [])}
    blocked = {
        index: result
        for index, line in enumerate(proposed)
        if (result := _blocked(line, catalog, allowed)) is not None
    }
    valid = [catalog.get(line.code) for i, line in enumerate(proposed) if i not in blocked]
    valid_codes = {row.code for row in valid}

    missing = find_missing(list(rules), valid, catalog)
    incomplete = {row.code: gap for gap in reversed(missing) for row in gap.triggered_by}
    companion_of = {
        row.code: rule
        for rule in rules
        for row in valid
        if rule.require.matches(row)
        and any(rule.when.matches(other) for other in valid if other.code != row.code)
    }

    ranked = matcher.rank(finding) if finding.strip() else []
    by_code = {candidate.row.code: candidate for candidate in ranked}
    rival = next((c for c in ranked if c.row.code not in valid_codes), None)

    results = []
    for index, line in enumerate(proposed):
        if index in blocked:
            results.append(blocked[index])
            continue
        row = catalog.get(line.code)
        if row.code in companion_of:
            status, reason = Status.PASSED, f"Required by rule '{companion_of[row.code].name}'."
        elif not finding.strip():
            status, reason = Status.PASSED, "Exists in the catalog (no finding text to compare with)."
        else:
            supported, reason = judge(by_code.get(row.code), rival)
            if row.code not in by_code:
                reason = f"No word of the finding points at {row.code}."
            status = Status.PASSED if supported else Status.NEEDS_PERSON
        if status is Status.PASSED and row.code in incomplete:
            gap = incomplete[row.code]
            options = " or ".join(r.code for r in gap.satisfied_by) or "a line this catalog lacks"
            status = Status.INCOMPLETE
            reason = f"Rule '{gap.rule.name}' also requires {options}, which is not in the set."
        results.append(LineResult(row.code, status, reason, row))
    return CheckReport(finding, tuple(results), tuple(missing))
