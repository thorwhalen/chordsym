"""The golden cases in fixtures/cases.json, run against the Python twin (the TS twin runs them too)."""

import pytest

from chordsym._fixtures import (
    CASES_PATH,
    REPO_ROOT,
    load,
    public_functions,
    run_case,
    same,
)

DATA = load() if (REPO_ROOT / CASES_PATH).exists() else {"functions": [], "cases": []}
CASES = DATA["cases"]
needs_fixtures = pytest.mark.skipif(
    not CASES, reason="fixtures/cases.json not present (installed package)"
)


@needs_fixtures
@pytest.mark.parametrize(
    "case", CASES, ids=lambda c: f"{c['fn']}{c.get('args')!r}"[:80]
)
def test_case(case):
    assert same(run_case(case), case["expected"])


@needs_fixtures
def test_cases_cover_exactly_the_public_functions():
    assert DATA["functions"] == list(public_functions())
    assert {c["fn"] for c in CASES} == set(public_functions())


@needs_fixtures
def test_order_matters():
    table = next(c for c in CASES if c["fn"] == "transposition_table")
    reordered = dict(table["expected"], chords=table["expected"]["chords"][::-1])
    assert len(table["expected"]["chords"]) < 2 or not same(
        table["expected"], reordered
    )
