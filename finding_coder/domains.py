"""Domain packs: a catalog plus optional rules and synonyms, loaded from a folder."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .catalog import Catalog, load_catalog, parse_catalog
from .matcher import Matcher, Synonyms, load_synonyms
from .rules import Rule, check_rules_fit_catalog, load_rules

DOMAINS_DIR = Path(__file__).resolve().parent.parent / "domains"


@dataclass(frozen=True)
class DomainPack:
    """Everything needed to match and check findings for one catalog."""

    name: str
    catalog: Catalog
    matcher: Matcher
    rules: tuple[Rule, ...]
    has_rules_file: bool
    folder: Path | None = None


def list_domains() -> list[str]:
    """Names of the bundled domain packs."""
    return sorted(p.name for p in DOMAINS_DIR.iterdir() if (p / "catalog.csv").is_file())


def load_domain(name_or_path: str) -> DomainPack:
    """Load a pack by bundled name ('rv_service') or by path to a folder.

    The folder must contain catalog.csv; rules.yaml and synonyms.yaml are optional.
    """
    folder = Path(name_or_path)
    if not (folder / "catalog.csv").is_file():
        folder = DOMAINS_DIR / name_or_path
    if not (folder / "catalog.csv").is_file():
        raise FileNotFoundError(
            f"No domain {name_or_path!r}. Bundled domains: {', '.join(list_domains())}; "
            "or pass a folder that contains catalog.csv."
        )
    catalog = load_catalog(folder / "catalog.csv")
    synonyms_file = folder / "synonyms.yaml"
    synonyms = load_synonyms(synonyms_file) if synonyms_file.is_file() else Synonyms()
    rules_file = folder / "rules.yaml"
    rules = load_rules(rules_file) if rules_file.is_file() else []
    check_rules_fit_catalog(rules, catalog)
    return DomainPack(
        folder.name, catalog, Matcher(catalog, synonyms), tuple(rules), rules_file.is_file(), folder
    )


def pack_from_catalog_text(text: str, name: str = "uploaded catalog") -> DomainPack:
    """Build a pack from catalog CSV text alone: no rules, no synonyms."""
    catalog = parse_catalog(text)
    return DomainPack(name, catalog, Matcher(catalog), (), False)
