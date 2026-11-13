"""Load and validate a code catalog from CSV (columns: code, section, description, hours)."""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from pathlib import Path

REQUIRED_COLUMNS = ("code", "section", "description", "hours")


class CatalogError(ValueError):
    """Raised when a catalog cannot be used. `problems` lists every issue found."""

    def __init__(self, problems: list[str]):
        self.problems = problems
        super().__init__("Catalog is not usable:\n- " + "\n- ".join(problems))


@dataclass(frozen=True)
class CatalogRow:
    """One line item of the catalog."""

    code: str
    section: str
    description: str
    hours: float


class Catalog:
    """A validated catalog with exact lookup by code."""

    def __init__(self, rows: list[CatalogRow]):
        self.rows = rows
        self._by_code = {row.code: row for row in rows}

    def __len__(self) -> int:
        return len(self.rows)

    def get(self, code: str) -> CatalogRow | None:
        """Return the row with exactly this code, or None. No fuzzy matching here."""
        return self._by_code.get(code)

    def codes(self) -> list[str]:
        return list(self._by_code)

    def sections(self) -> list[str]:
        return sorted({row.section for row in self.rows})


def parse_catalog(text: str) -> Catalog:
    """Parse CSV text into a Catalog. Lines starting with '#' are comments.

    Every problem in the file is collected and reported together, with line
    numbers, so a person can fix the file in one pass.
    """
    if len(text) > 1_000_000:
        raise CatalogError(["catalog exceeds 1 MB"])
    reader = csv.reader(io.StringIO(text.lstrip("\ufeff")), strict=True)
    numbered = []
    try:
        for values in reader:
            if not values or not any(v.strip() for v in values):
                continue
            if values[0].lstrip().startswith("#"):
                continue
            numbered.append((reader.line_num, values))
    except csv.Error as error:
        raise CatalogError([f"line {reader.line_num}: malformed CSV: {error}"]) from error
    if not numbered:
        raise CatalogError(["the file has no rows"])
    header_number, header_values = numbered[0]
    header = [name.strip().lower() for name in header_values]
    if len(set(header)) != len(header):
        raise CatalogError([f"line {header_number}: duplicate column names"])
    absent = [name for name in REQUIRED_COLUMNS if name not in header]
    if absent:
        raise CatalogError([f"line {header_number}: header is missing column(s): {', '.join(absent)}"])
    if len(numbered) > 1001:
        raise CatalogError(["catalog exceeds 1,000 rows"])

    problems: list[str] = []
    rows: list[CatalogRow] = []
    first_seen: dict[str, int] = {}
    for number, values in numbered[1:]:
        if len(values) != len(header):
            problems.append(
                f"line {number}: expected {len(header)} columns, found {len(values)}"
            )
            continue
        record = {name: value.strip() for name, value in zip(header, values)}
        empty = [name for name in REQUIRED_COLUMNS if not record[name]]
        if empty:
            problems.append(f"line {number}: empty field(s): {', '.join(empty)}")
            continue
        code = record["code"]
        if code in first_seen:
            problems.append(
                f"line {number}: duplicate code {code!r} (first used on line {first_seen[code]})"
            )
            continue
        first_seen[code] = number
        try:
            hours = float(record["hours"])
        except ValueError:
            problems.append(f"line {number}: hours {record['hours']!r} is not a number")
            continue
        if not 0 <= hours < float("inf"):
            problems.append(f"line {number}: hours {record['hours']!r} must be zero or more")
            continue
        rows.append(CatalogRow(code, record["section"], record["description"], hours))

    if not rows and not problems:
        problems.append("the file has a header but no rows")
    if problems:
        raise CatalogError(problems)
    return Catalog(rows)


def load_catalog(path: str | Path) -> Catalog:
    """Read and validate a catalog CSV file."""
    return parse_catalog(Path(path).read_text(encoding="utf-8"))
