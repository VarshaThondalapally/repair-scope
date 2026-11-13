"""Triage a batch of findings into coded lines and a review queue for a person."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from .domains import DomainPack
from .export import ExportLine
from .matcher import Candidate
from .rules import find_missing

QUEUE_FIELDS = ("finding", "why", "candidate_1", "candidate_2", "candidate_3")


@dataclass(frozen=True)
class ReviewItem:
    """A finding the tool will not code on its own, with the reason and its best guesses."""

    finding: str
    why: str
    candidates: tuple[Candidate, ...]


def triage(pack: DomainPack, findings: list[str]) -> tuple[list[ExportLine], list[ReviewItem]]:
    """Queue every finding. Relevance never authorizes billable work."""
    queue = []
    for finding in findings:
        result = pack.matcher.match(finding, k=3)
        queue.append(ReviewItem(finding, "Human approval required. " + result.reason, result.candidates))
    return [], queue


def write_queue(path: str | Path, queue: list[ReviewItem]) -> None:
    """Write the review queue as CSV: finding, reason, and up to three candidates."""
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(QUEUE_FIELDS)
        for item in queue:
            guesses = [f"{c.row.code} {c.row.description}" for c in item.candidates[:3]]
            writer.writerow([item.finding, item.why, *guesses, *[""] * (3 - len(guesses))])
