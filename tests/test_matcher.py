import pytest

from finding_coder.catalog import parse_catalog
from finding_coder.matcher import MARGIN, Matcher, Synonyms, load_synonyms, stem, tokenize


@pytest.mark.parametrize(
    "word, expected",
    [
        ("leaks", "leak"),
        ("leaking", "leak"),
        ("leaked", "leak"),
        ("batteries", "battery"),
        ("switches", "switch"),
        ("dripping", "drip"),
        ("replaced", "replac"),
        ("replace", "replac"),
        ("gas", "gas"),
        ("glass", "glass"),
    ],
)
def test_stem(word, expected):
    assert stem(word) == expected


def test_tokenize_drops_stopwords_and_joins_slash_abbreviations():
    assert tokenize("The A/C is leaking on the roof") == ["ac", "leak", "roof"]
    assert tokenize("won't light") == ["wont", "light"]


def test_best_row_ranks_first(matcher):
    result = matcher.match("roof vent lid cracked")
    assert result.candidates[0].row.code == "R-2"
    assert [c.score for c in result.candidates] == sorted(
        (c.score for c in result.candidates), reverse=True
    )


def test_matched_terms_explain_the_suggestion(matcher):
    top = matcher.match("water pump is dead").candidates[0]
    assert top.row.code == "W-1"
    assert {term.source for term in top.matched} == {"water", "pump"}
    assert not any(term.via_synonym for term in top.matched)


def test_synonym_reaches_a_row_the_plain_words_miss(catalog):
    finding = "propane regulator hissing"
    plain = Matcher(catalog).rank(finding)[0]
    assert {term.term for term in plain.matched} == {"regulator"}

    with_synonyms = Matcher(catalog, Synonyms([["propane", "gas"]])).rank(finding)[0]
    by_term = {term.term: term for term in with_synonyms.matched}
    assert by_term["gas"].via_synonym and by_term["gas"].source == "propane"
    assert by_term["gas"].label == "gas (synonym of 'propane')"
    assert with_synonyms.score > plain.score


def test_phrase_synonym(matcher):
    top = matcher.match("water heater won't light").candidates[0]
    assert top.row.code == "W-2"
    assert any(term.term == "igniter" and term.via_synonym for term in top.matched)


def test_top_k_limits_candidates(matcher):
    assert len(matcher.match("replace", k=3).candidates) == 3


def test_no_shared_word_needs_a_person(matcher):
    result = matcher.match("customer unhappy about paint colour")
    assert result.candidates == ()
    assert not result.confident
    assert "No catalog row" in result.reason


def test_single_matched_word_needs_a_person(matcher):
    result = matcher.match("pump")
    assert result.candidates[0].row.code == "W-1"
    assert not result.confident
    assert "Only one word" in result.reason


def test_close_runner_up_needs_a_person(matcher):
    result = matcher.match("roof vent")
    top, second = result.candidates[:2]
    assert top.score < MARGIN * second.score
    assert not result.confident
    assert "Too close to call" in result.reason


def test_clear_winner_is_confident(matcher):
    result = matcher.match("gas regulator hissing at the bottles")
    assert result.candidates[0].row.code == "G-1"
    assert result.confident


def test_single_row_catalog_can_be_confident():
    catalog = parse_catalog("code,section,description,hours\nA-1,Roof,Reseal roof vent,1\n")
    assert Matcher(catalog).match("reseal the vent").confident


def test_load_synonyms_rejects_wrong_shape(tmp_path):
    good = tmp_path / "good.yaml"
    good.write_text("groups:\n  - [propane, lp]\n", encoding="utf-8")
    assert load_synonyms(good).expand(tokenize("propane tank")) == {"lp": ("lp", "propane")}

    bad = tmp_path / "bad.yaml"
    bad.write_text("groups:\n  - propane\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_synonyms(bad)
