"""Measure the matcher and the rules against each domain's gold findings.

Run:  python -m finding_coder.evaluate            (all bundled domains)
      python -m finding_coder.evaluate --domain rv_service
Prints a table and writes EVAL.md for the domains that were run.
"""

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass, field
from pathlib import Path

from .domains import DomainPack, list_domains, load_domain
from .matcher import MARGIN, MIN_MATCHED_TERMS, Candidate
from .rules import find_missing

WORST = 5


@dataclass(frozen=True)
class GoldCase:
    finding: str
    expected: tuple[str, ...]
    companions: tuple[str, ...]


@dataclass(frozen=True)
class Miss:
    """A gold finding whose expected code was not the top pick."""

    case: GoldCase
    rank: int | None  # rank of the best expected code, None if it was not ranked at all
    top: Candidate | None
    expected_candidate: Candidate | None

    def explain(self) -> str:
        top = (
            f"top pick was {self.top.row.code} '{self.top.row.description}' "
            f"on [{', '.join(t.label for t in self.top.matched)}]"
            if self.top
            else "nothing was ranked"
        )
        if self.expected_candidate is None:
            return f"The expected row shares no word or listed synonym with the finding; {top}."
        words = ", ".join(t.label for t in self.expected_candidate.matched)
        return f"Expected row ranked #{self.rank}, matching only [{words}]; {top}."


@dataclass
class Scores:
    domain: str
    total: int = 0
    top1: int = 0
    top3: int = 0
    needs_person: int = 0
    confident_right: int = 0
    needs_person_right: int = 0
    rule_cases: int = 0
    rules_caught: int = 0
    rules_caught_from_top1: int = 0
    no_companion_cases: int = 0
    extra_demands: int = 0
    misses: list[Miss] = field(default_factory=list)

    @property
    def confident(self) -> int:
        return self.total - self.needs_person


def load_gold(path: Path) -> list[GoldCase]:
    """Read gold.csv: finding, expected_codes, expected_companions (';' separated)."""
    with open(path, newline="", encoding="utf-8") as handle:
        return [
            GoldCase(
                record["finding"],
                tuple(code for code in record["expected_codes"].split(";") if code),
                tuple(code for code in record["expected_companions"].split(";") if code),
            )
            for record in csv.DictReader(handle)
        ]


def _suggested(pack: DomainPack, codes: tuple[str, ...]) -> set[str]:
    """Codes the rules ask for when exactly `codes` are selected."""
    rows = [pack.catalog.get(code) for code in codes]
    gaps = find_missing(list(pack.rules), rows, pack.catalog)
    return {row.code for gap in gaps for row in gap.satisfied_by}


def evaluate(pack: DomainPack, cases: list[GoldCase]) -> Scores:
    """Score one domain. Gold codes that are not in the catalog are a hard error."""
    scores = Scores(pack.name, total=len(cases))
    for case in cases:
        unknown = [c for c in case.expected + case.companions if pack.catalog.get(c) is None]
        if unknown:
            raise ValueError(f"gold finding {case.finding!r} uses unknown code(s) {unknown}")

        ranked = pack.matcher.rank(case.finding)
        result = pack.matcher.match(case.finding)
        codes = [candidate.row.code for candidate in ranked]
        hit1 = bool(codes) and codes[0] in case.expected
        scores.top1 += hit1
        scores.top3 += any(code in case.expected for code in codes[:3])
        if result.confident:
            scores.confident_right += hit1
        else:
            scores.needs_person += 1
            scores.needs_person_right += hit1
        if not hit1:
            ranks = [codes.index(code) + 1 for code in case.expected if code in codes]
            rank = min(ranks) if ranks else None
            scores.misses.append(
                Miss(case, rank, ranked[0] if ranked else None, ranked[rank - 1] if rank else None)
            )

        if case.companions:
            scores.rule_cases += 1
            scores.rules_caught += set(case.companions) <= _suggested(pack, case.expected)
            scores.rules_caught_from_top1 += bool(codes) and set(case.companions) <= _suggested(
                pack, (codes[0],)
            )
        else:
            scores.no_companion_cases += 1
            scores.extra_demands += bool(_suggested(pack, case.expected))
    scores.misses.sort(key=lambda miss: -(miss.rank or 10**6))
    return scores


def table(all_scores: list[Scores]) -> str:
    """Markdown table of the headline numbers, one column per domain."""

    def row(label: str, cell) -> str:
        return f"| {label} | " + " | ".join(cell(s) for s in all_scores) + " |"

    def share(count: int, total: int) -> str:
        return f"{count}/{total} ({count / total:.0%})" if total else "0/0"

    return "\n".join(
        [
            "| Measure | " + " | ".join(s.domain for s in all_scores) + " |",
            "|---|" + "---|" * len(all_scores),
            row("Gold findings", lambda s: str(s.total)),
            row("Top-1 hit (top pick is the expected code)", lambda s: share(s.top1, s.total)),
            row("Top-3 hit (expected code in first three)", lambda s: share(s.top3, s.total)),
            row("Routed to 'needs a person'", lambda s: share(s.needs_person, s.total)),
            row("Called confident", lambda s: share(s.confident, s.total)),
            row(
                "Confident and correct (of those called confident)",
                lambda s: share(s.confident_right, s.confident),
            ),
            row(
                "Routed to a person although top pick was correct",
                lambda s: share(s.needs_person_right, s.needs_person),
            ),
            row(
                "Incomplete sets caught, given the correct code",
                lambda s: share(s.rules_caught, s.rule_cases),
            ),
            row(
                "Incomplete sets caught, starting from the matcher's top pick",
                lambda s: share(s.rules_caught_from_top1, s.rule_cases),
            ),
            row(
                "Rule fired where gold expects no companion",
                lambda s: share(s.extra_demands, s.no_companion_cases),
            ),
        ]
    )


def report(all_scores: list[Scores], command: str) -> str:
    """Full EVAL.md text."""
    parts = [
        "# Evaluation",
        "",
        "Produced by this command, not edited by hand:",
        "",
        f"    {command}",
        "",
        f"Confident rule in force: at least {MIN_MATCHED_TERMS} matched words and a score at "
        f"least {MARGIN}x the runner-up.",
        "",
        table(all_scores),
        "",
        "How to read it: the gold findings, the catalog, the synonyms and the rules were all "
        "written by the same author, and the data is invented. The numbers show how this "
        "matcher behaves on these files. They are not evidence of accuracy on a real shop's data.",
        "",
        "'Incomplete sets caught' counts a gold finding only if the rules ask for every "
        "companion line the gold file lists.",
    ]
    for scores in all_scores:
        parts += ["", f"## {scores.domain}: {WORST} worst misses", ""]
        if not scores.misses:
            parts.append("No misses.")
        for miss in scores.misses[:WORST]:
            expected = ", ".join(miss.case.expected)
            parts.append(f"- \"{miss.case.finding}\" (expected {expected}). {miss.explain()}")
        parts += ["", f"Total top-1 misses in this domain: {len(scores.misses)}."]
    return "\n".join(parts) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="finding_coder.evaluate", description=__doc__)
    parser.add_argument(
        "--domain", action="append", help="domain to evaluate (repeatable; default: all bundled)"
    )
    parser.add_argument("--out", default="EVAL.md", help="where to write the report")
    args = parser.parse_args(argv)
    arguments = sys.argv[1:] if argv is None else argv

    all_scores = []
    for name in args.domain or list_domains():
        pack = load_domain(name)
        all_scores.append(evaluate(pack, load_gold(pack.folder / "gold.csv")))
    command = " ".join(["python -m finding_coder.evaluate", *arguments])
    text = report(all_scores, command)
    Path(args.out).write_text(text, encoding="utf-8")
    print(text)
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
