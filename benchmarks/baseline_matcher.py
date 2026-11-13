"""Rank catalog rows for a free-text finding with BM25, and say how sure the ranking is.

This is word matching, not language understanding. A row is suggested because
it shares words (or listed synonyms) with the finding, and every suggestion
carries those words so a person can see why it was made.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import yaml

from finding_coder.catalog import Catalog, CatalogRow

# BM25 constants (the usual textbook values).
K1 = 1.5
B = 0.75
# A word that only matched through the synonyms file counts a bit less than a
# word the technician actually wrote.
SYNONYM_WEIGHT = 0.6

# The "confident" rule. A top pick is confident only when BOTH hold:
#   1. at least MIN_MATCHED_TERMS different words of the finding point at it, and
#   2. its score is at least MARGIN times the score of the best competing row.
# Anything else is routed to a person.
MIN_MATCHED_TERMS = 2
MARGIN = 1.2

STOPWORDS = frozenset(
    "a an and are as at be been but by for from had has have in is it its of on or "
    "that the then there this to was were when with".split()
)

_WORD = re.compile(r"[a-z0-9]+")
_SLASH_ABBREVIATION = re.compile(r"\b([a-z])/([a-z])\b")


def stem(word: str) -> str:
    """Reduce a lowercase word to a rough base form.

    Strips plurals, then '-ing' / '-ed', then a trailing 'e', so that
    'leaks', 'leaking' and 'leaked' all become 'leak'. Deliberately crude:
    it only has to be applied the same way to findings and to the catalog.
    """
    if len(word) > 4 and word.endswith("ies"):
        word = word[:-3] + "y"
    elif len(word) > 4 and word.endswith(("ches", "shes", "sses", "xes", "zes")):
        word = word[:-2]
    elif len(word) > 3 and word.endswith("s") and not word.endswith(("ss", "us", "is")):
        word = word[:-1]
    for suffix in ("ing", "ed"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            word = word[: -len(suffix)]
            if len(word) > 3 and word[-1] == word[-2] and word[-1] not in "ls":
                word = word[:-1]  # dripp -> drip
            break
    if len(word) > 4 and word.endswith("e"):
        word = word[:-1]
    return word


def words(text: str) -> list[str]:
    """Lowercase surface words of a text, without stopwords. 'a/c' becomes 'ac'."""
    text = text.lower().replace("'", "").replace("’", "")
    text = _SLASH_ABBREVIATION.sub(r"\1\2", text)
    return [word for word in _WORD.findall(text) if word not in STOPWORDS]


def tokenize(text: str) -> list[str]:
    """Stemmed words of a text, in order."""
    return [stem(word) for word in words(text)]


def contains_phrase(tokens: list[str], phrase: tuple[str, ...]) -> bool:
    """True when `phrase` appears in `tokens` as a run of neighbouring words."""
    size = len(phrase)
    return size > 0 and any(
        tuple(tokens[start : start + size]) == phrase
        for start in range(len(tokens) - size + 1)
    )


class Synonyms:
    """Groups of words or short phrases that mean the same thing in one trade."""

    def __init__(self, groups: list[list[str]] | None = None):
        self.groups = [
            [(phrase, tuple(words(phrase))) for phrase in group] for group in (groups or [])
        ]

    def expand(self, tokens: list[str]) -> dict[str, tuple[str, str]]:
        """Return extra words to search for.

        Maps each extra stemmed word to (the word as written in the synonyms
        file, the finding phrase that caused it).
        """
        extra: dict[str, tuple[str, str]] = {}
        for group in self.groups:
            present = [
                phrase
                for phrase, surface in group
                if contains_phrase(tokens, tuple(stem(word) for word in surface))
            ]
            if not present:
                continue
            for _, surface in group:
                for word in surface:
                    if stem(word) not in tokens:
                        extra.setdefault(stem(word), (word, present[0]))
        return extra


def load_synonyms(path: str | Path) -> Synonyms:
    """Load a synonyms YAML file of the form `groups: [[word, phrase, ...], ...]`."""
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    groups = data.get("groups", []) if isinstance(data, dict) else None
    if not isinstance(groups, list) or not all(
        isinstance(group, list) and all(isinstance(item, str) for item in group)
        for group in groups
    ):
        raise ValueError(f"{path}: expected 'groups:' to be a list of lists of words")
    return Synonyms(groups)


@dataclass(frozen=True)
class MatchedTerm:
    """One reason a row was suggested."""

    term: str  # the stemmed word found in the catalog row
    word: str  # the same word as a person wrote it (in the finding or the synonyms file)
    source: str  # the word or phrase in the finding that led to it
    via_synonym: bool

    @property
    def label(self) -> str:
        return f"{self.word} (synonym of '{self.source}')" if self.via_synonym else self.word


@dataclass(frozen=True)
class Candidate:
    """A catalog row with its score for one finding and the words that earned it."""

    row: CatalogRow
    score: float
    matched: tuple[MatchedTerm, ...]


@dataclass(frozen=True)
class MatchResult:
    """Ranked candidates for one finding plus the confident / needs-a-person verdict."""

    finding: str
    candidates: tuple[Candidate, ...]
    confident: bool
    reason: str


def judge(candidate: Candidate | None, rival: Candidate | None) -> tuple[bool, str]:
    """Apply the confident rule to `candidate` against its best competing row."""
    if candidate is None:
        return False, "No catalog row shares a word with this finding."
    if len(candidate.matched) < MIN_MATCHED_TERMS:
        return False, (
            f"Only one word of the finding ('{candidate.matched[0].label}') "
            f"points at {candidate.row.code}."
        )
    if rival is not None and candidate.score < rival.score:
        return False, (
            f"Another row fits the wording better: {rival.row.code} scores {rival.score:.2f} "
            f"and {candidate.row.code} scores {candidate.score:.2f}."
        )
    if rival is not None and candidate.score < MARGIN * rival.score:
        return False, (
            f"Too close to call: {candidate.row.code} scores {candidate.score:.2f} "
            f"and {rival.row.code} scores {rival.score:.2f}."
        )
    return True, (
        f"{len(candidate.matched)} words of the finding point at {candidate.row.code} "
        f"and no other row comes within {round((MARGIN - 1) * 100)}% of its score."
    )


class Matcher:
    """BM25 index over 'description + section' of every catalog row."""

    def __init__(self, catalog: Catalog, synonyms: Synonyms | None = None):
        self.catalog = catalog
        self.synonyms = synonyms or Synonyms()
        self._docs = [
            Counter(tokenize(f"{row.description} {row.section}")) for row in catalog.rows
        ]
        self._lengths = [sum(doc.values()) for doc in self._docs]
        self._average_length = sum(self._lengths) / len(self._lengths)
        document_frequency = Counter(token for doc in self._docs for token in doc)
        total = len(self._docs)
        self._idf = {
            token: math.log(1 + (total - count + 0.5) / (count + 0.5))
            for token, count in document_frequency.items()
        }

    def rank(self, finding: str) -> list[Candidate]:
        """All rows that share at least one word with the finding, best first."""
        surface = words(finding)
        tokens = [stem(word) for word in surface]
        query = {
            token: MatchedTerm(token, word, word, False) for word, token in zip(surface, tokens)
        }
        for token, (word, phrase) in self.synonyms.expand(tokens).items():
            query[token] = MatchedTerm(token, word, phrase, True)

        candidates = []
        for row, doc, length in zip(self.catalog.rows, self._docs, self._lengths):
            score = 0.0
            matched = []
            for token, term in query.items():
                frequency = doc.get(token, 0)
                if not frequency:
                    continue
                weight = SYNONYM_WEIGHT if term.via_synonym else 1.0
                saturation = frequency * (K1 + 1) / (
                    frequency + K1 * (1 - B + B * length / self._average_length)
                )
                score += weight * self._idf[token] * saturation
                matched.append(term)
            if matched:
                candidates.append(Candidate(row, score, tuple(matched)))
        candidates.sort(key=lambda candidate: (-candidate.score, candidate.row.code))
        return candidates

    def match(self, finding: str, k: int = 5) -> MatchResult:
        """Top-k candidates and whether the top one can be trusted without a person."""
        ranked = self.rank(finding)
        top = ranked[0] if ranked else None
        runner_up = ranked[1] if len(ranked) > 1 else None
        confident, reason = judge(top, runner_up)
        return MatchResult(finding, tuple(ranked[:k]), confident, reason)
