"""Command line: match, check, batch, serve."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .catalog import CatalogError
from .checker import CheckReport, ProposedLine, check
from .domains import load_domain
from .export import write_csv
from .review import triage, write_queue
from .rules import RulesError


def _print_report(report: CheckReport, has_rules_file: bool) -> None:
    print("Line status:")
    for line in report.lines:
        print(f"  {line.code:<10} {line.status.value.upper()}: {line.reason}")
    print("Completeness:")
    if not has_rules_file:
        print("  no rules loaded for this catalog")
    elif report.complete:
        print("  complete: no rule is unmet")
    for gap in report.missing:
        print(f"  MISSING  {gap.rule.name}")
        print(f"           why: {gap.rule.reason}")
        for row in gap.satisfied_by:
            print(f"           add: {row.code}  {row.description} ({row.hours:g} h)")


def cmd_match(args: argparse.Namespace) -> None:
    pack = load_domain(args.domain)
    result = pack.matcher.match(args.finding, k=args.top)
    print(f"Finding: {args.finding}")
    print(f"Catalog: {pack.name} ({len(pack.catalog)} rows, {len(pack.rules)} rules)\n")
    if not result.candidates:
        print("No candidates. " + result.reason)
        return
    print(f"{'#':<3}{'score':>6}  {'code':<10}{'section':<26}description")
    for rank, candidate in enumerate(result.candidates, start=1):
        row = candidate.row
        print(f"{rank:<3}{candidate.score:>6.2f}  {row.code:<10}{row.section:<26}{row.description}")
        print(f"{'':<11}matched: {', '.join(term.label for term in candidate.matched)}")
    verdict = "CONFIDENT" if result.confident else "NEEDS A PERSON"
    print(f"\nVerdict on the top pick: {verdict}. {result.reason}\n")
    top = result.candidates[0].row.code
    print(f"Check of the top pick alone ({top}):")
    report = check(args.finding, [ProposedLine(top)], pack.catalog, pack.matcher, pack.rules)
    _print_report(report, pack.has_rules_file)


def cmd_check(args: argparse.Namespace) -> None:
    pack = load_domain(args.domain)
    proposed = [ProposedLine(code) for code in args.codes]
    report = check(
        args.finding, proposed, pack.catalog, pack.matcher, pack.rules, args.section or None
    )
    print(f"Finding: {args.finding}")
    _print_report(report, pack.has_rules_file)


def cmd_batch(args: argparse.Namespace) -> None:
    pack = load_domain(args.domain)
    text = Path(args.findings_file).read_text(encoding="utf-8")
    findings = [line.strip() for line in text.splitlines() if line.strip()]
    coded, queue = triage(pack, findings)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    write_csv(out / "coded.csv", coded)
    write_queue(out / "review_queue.csv", queue)
    print(f"{len(findings)} findings: {len(findings) - len(queue)} coded, {len(queue)} for review")
    print(f"wrote {out / 'coded.csv'} ({len(coded)} lines) and {out / 'review_queue.csv'}")


def cmd_serve(args: argparse.Namespace) -> None:
    import uvicorn

    uvicorn.run("finding_coder.server:app", host=args.host, port=args.port)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="finding_coder", description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    domain_help = "bundled domain name, or a folder containing catalog.csv"

    match = commands.add_parser("match", help="rank catalog rows for one finding")
    match.add_argument("--domain", required=True, help=domain_help)
    match.add_argument("--top", type=int, default=5, help="how many candidates to show")
    match.add_argument("finding")
    match.set_defaults(run=cmd_match)

    checker = commands.add_parser("check", help="check codes you already have for a finding")
    checker.add_argument("--domain", required=True, help=domain_help)
    checker.add_argument(
        "--section", action="append", help="section the finding belongs to (repeatable)"
    )
    checker.add_argument("finding")
    checker.add_argument("codes", nargs="+")
    checker.set_defaults(run=cmd_check)

    batch = commands.add_parser("batch", help="code a file of findings, one per line")
    batch.add_argument("--domain", required=True, help=domain_help)
    batch.add_argument("--out", default="out", help="folder for coded.csv and review_queue.csv")
    batch.add_argument("findings_file")
    batch.set_defaults(run=cmd_batch)

    serve = commands.add_parser("serve", help="start the local web page")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)
    serve.set_defaults(run=cmd_serve)

    args = parser.parse_args(argv)
    try:
        args.run(args)
    except (CatalogError, RulesError, FileNotFoundError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
