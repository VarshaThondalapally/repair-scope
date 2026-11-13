"""Write approved lines to CSV."""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from pathlib import Path

from .catalog import CatalogRow
from .checker import CheckReport, Status

FIELDS = ("finding", "code", "section", "description", "hours", "note")


def safe_cell(value):
    """Keep untrusted text from executing as a spreadsheet formula."""
    value = str(value)
    return "'" + value if value.lstrip().startswith(("=", "+", "-", "@")) or value.startswith(("\t", "\r", "\n")) else value


class ExportError(ValueError):
    """Raised when a checked set must not be exported as it stands."""


@dataclass(frozen=True)
class ExportLine:
    finding: str
    row: CatalogRow
    note: str


def approved_lines(
    report: CheckReport,
    reviewed: frozenset[str] | set[str] = frozenset(),
    allow_incomplete: bool = False,
) -> list[ExportLine]:
    """Pick the lines of a check report that may be exported.

    Blocked lines are never exported. A 'needs a person' line is exported only
    if its code is in `reviewed`. An incomplete set is refused unless
    `allow_incomplete` is set by the caller.
    """
    if report.missing and not allow_incomplete:
        names = ", ".join(f"'{gap.rule.name}'" for gap in report.missing)
        raise ExportError(f"The set is incomplete; unmet rule(s): {names}.")
    lines = []
    for line in report.lines:
        if line.status.blocked:
            continue
        if line.status is Status.NEEDS_PERSON and line.code not in reviewed:
            continue
        note = "reviewed by a person" if line.status is Status.NEEDS_PERSON else line.status.value
        lines.append(ExportLine(report.finding, line.row, note))
    return lines


def to_csv(lines: list[ExportLine]) -> str:
    """Render export lines as CSV text with a header row."""
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(FIELDS)
    for line in lines:
        row = line.row
        writer.writerow(
            [safe_cell(v) for v in (line.finding, row.code, row.section, row.description, f"{row.hours:g}", line.note)]
        )
    return buffer.getvalue()


def write_csv(path: str | Path, lines: list[ExportLine]) -> None:
    """Write export lines to a CSV file."""
    Path(path).write_text(to_csv(lines), encoding="utf-8")
