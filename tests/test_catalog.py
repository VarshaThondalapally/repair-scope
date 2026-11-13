import pytest

from finding_coder.catalog import CatalogError, load_catalog, parse_catalog

HEADER = "code,section,description,hours\n"


def test_valid_catalog_loads(catalog):
    assert len(catalog) == 8
    assert catalog.get("G-2").description == "Gas leak test"
    assert catalog.get("G-2").hours == 0.4
    assert catalog.sections() == ["Diagnosis", "Gas", "Roof", "Water"]


def test_lookup_is_exact(catalog):
    assert catalog.get("g-2") is None
    assert catalog.get("G-2 ") is None
    assert catalog.get("G-9") is None


def test_comment_lines_and_header_case_are_tolerated():
    catalog = parse_catalog("# a note\nCode, Section ,Description,HOURS\nA-1,S,Thing,1\n")
    assert catalog.get("A-1").hours == 1.0


def test_duplicate_code_is_reported_with_both_lines():
    with pytest.raises(CatalogError) as error:
        parse_catalog(HEADER + "A-1,S,One,1\nA-1,S,Two,2\n")
    assert error.value.problems == ["line 3: duplicate code 'A-1' (first used on line 2)"]


@pytest.mark.parametrize("hours", ["abc", "-1", "nan", "inf"])
def test_bad_hours_are_rejected(hours):
    with pytest.raises(CatalogError) as error:
        parse_catalog(HEADER + f"A-1,S,One,{hours}\n")
    assert "hours" in error.value.problems[0]


def test_empty_field_is_reported():
    with pytest.raises(CatalogError) as error:
        parse_catalog(HEADER + "A-1,,One,1\n")
    assert error.value.problems == ["line 2: empty field(s): section"]


def test_missing_column_is_reported():
    with pytest.raises(CatalogError) as error:
        parse_catalog("code,description,hours\nA-1,One,1\n")
    assert "missing column(s): section" in error.value.problems[0]


def test_wrong_column_count_is_reported():
    with pytest.raises(CatalogError) as error:
        parse_catalog(HEADER + "A-1,S,One with, a comma,1\n")
    assert "expected 4 columns, found 5" in error.value.problems[0]


def test_all_problems_are_collected_in_one_pass():
    with pytest.raises(CatalogError) as error:
        parse_catalog(HEADER + "A-1,S,One,x\nA-2,,Two,1\nA-3,S,Three,1\nA-3,S,Again,1\n")
    assert len(error.value.problems) == 3


def test_empty_file_and_header_only_are_rejected():
    for text in ("", HEADER):
        with pytest.raises(CatalogError):
            parse_catalog(text)


def test_quoted_commas_are_fine_and_load_from_file(tmp_path):
    path = tmp_path / "c.csv"
    path.write_text(HEADER + 'A-1,S,"One, with a comma",1.5\n', encoding="utf-8")
    assert load_catalog(path).get("A-1").description == "One, with a comma"
