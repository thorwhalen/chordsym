"""The golden cases in fixtures/cases.json, run against the Python twin (the TS twin runs them too)."""

from pathlib import Path

import pytest

from chordsym._fixtures import load_cases, run_case

ROOT = Path(__file__).resolve().parent.parent
CASES = load_cases(ROOT) if (ROOT / "fixtures" / "cases.json").exists() else []


@pytest.mark.skipif(
    not CASES, reason="fixtures/cases.json not present (installed package)"
)
@pytest.mark.parametrize(
    "case", CASES, ids=lambda c: f"{c['fn']}{c.get('args')!r}"[:80]
)
def test_case(case):
    assert run_case(case) == case["expected"]


def test_cases_cover_every_public_function():
    from chordsym._fixtures import FUNCTIONS

    if CASES:
        assert {c["fn"] for c in CASES} == set(FUNCTIONS)
