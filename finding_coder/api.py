"""Plain-data views of matching and checking, shared by the web server and its tests."""

from __future__ import annotations

import re
import hashlib
import json

from .catalog import CatalogRow
from .checker import ProposedLine, check
from .domains import DomainPack
from .export import approved_lines, to_csv
from .matcher import STOPWORDS, stem
from .policy import review_guidance

_SPLIT = re.compile(r"([A-Za-z0-9]+)")


def highlight(text: str, terms: set[str]) -> list[list]:
    """Split `text` into [fragment, is_matched] pairs so a page can mark the matched words."""
    parts = []
    for fragment in _SPLIT.split(text):
        if fragment:
            word = fragment.lower()
            parts.append([fragment, word not in STOPWORDS and stem(word) in terms])
    return parts


def _row(row: CatalogRow) -> dict:
    return {
        "code": row.code,
        "section": row.section,
        "description": row.description,
        "hours": row.hours,
    }


def describe(pack: DomainPack) -> dict:
    """Summary of a pack for the page header."""
    return {
        "name": pack.name,
        "rows": len(pack.catalog),
        "sections": pack.catalog.sections(),
        "rules": len(pack.rules),
        "has_rules_file": pack.has_rules_file,
        "catalog_id": hashlib.sha256(json.dumps([_row(r) for r in pack.catalog.rows], sort_keys=True).encode()).hexdigest()[:16],
        "sample_data": pack.name in ("rv_service", "property_restoration"),
        "approval_required": True,
    }


def run_match(pack: DomainPack, finding: str, k: int = 8) -> dict:
    """Ranked candidates with highlight fragments and the confidence verdict."""
    result = pack.matcher.match(finding, k=k)
    candidates = []
    for candidate in result.candidates:
        terms = {term.term for term in candidate.matched}
        candidates.append(
            {
                **_row(candidate.row),
                "score": round(candidate.score, 2),
                "why": [term.label for term in candidate.matched],
                "description_parts": highlight(candidate.row.description, terms),
                "section_parts": highlight(candidate.row.section, terms),
            }
        )
    return {"candidates": candidates, "confident": result.confident, "reason": result.reason,
            "approval_required": True, "questions": review_guidance(finding, result.candidates),
            "strategy": pack.matcher.strategy, "catalog_id": describe(pack)["catalog_id"]}


def run_check(pack: DomainPack, finding: str, codes: list[str]) -> dict:
    """Per-line statuses and unmet completeness rules for the chosen codes."""
    report = check(
        finding, [ProposedLine(code) for code in codes], pack.catalog, pack.matcher, pack.rules
    )
    return {
        "lines": [
            {
                "code": line.code,
                "status": line.status.value,
                "blocked": line.status.blocked,
                "reason": line.reason,
                "row": _row(line.row) if line.row else None,
            }
            for line in report.lines
        ],
        "missing": [
            {
                "rule": gap.rule.name,
                "reason": gap.rule.reason,
                "triggered_by": [row.code for row in gap.triggered_by],
                "satisfied_by": [_row(row) for row in gap.satisfied_by],
            }
            for gap in report.missing
        ],
        "complete": report.complete,
        "has_rules_file": pack.has_rules_file,
        "rules": len(pack.rules),
    }


def run_export(pack: DomainPack, finding: str, codes: list[str], allow_incomplete: bool) -> str:
    """CSV text for lines a person ticked on the page (their tick counts as their review)."""
    report = check(
        finding, [ProposedLine(code) for code in codes], pack.catalog, pack.matcher, pack.rules
    )
    return to_csv(approved_lines(report, reviewed=set(codes), allow_incomplete=allow_incomplete))
