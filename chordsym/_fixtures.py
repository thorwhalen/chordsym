"""Run and record the golden cases in ``fixtures/cases.json``, the behaviour both twins must share.

A case is ``{"fn": <public function name>, "args": [...], "kwargs": {...}, "expected": ...}``
in JSON form: tuples are lists, a :class:`~chordsym.Key` is ``{"tonic": int, "minor": bool}``.
The Python tests (``tests/test_fixtures.py``) and the TypeScript tests
(``ts/src/fixtures.test.ts``) run every case.

To add a case, append it with any ``expected`` and run ``python -m chordsym._fixtures``
from the repository root: it rewrites every ``expected`` from the Python implementation,
so review the diff (a changed expectation is a behaviour change on both sides).

>>> run_case({"fn": "transpose_chord", "args": ["C/E", 3], "kwargs": {"flats": True}})
'Eb/G'
>>> run_case({"fn": "estimate_key", "args": [["Am", "Dm", "E7"]]})
{'tonic': 9, 'minor': True}
"""

from __future__ import annotations

import json
from pathlib import Path

import chordsym
from chordsym.keys import Key

#: The golden cases, relative to the repository root.
CASES_PATH = Path("fixtures") / "cases.json"

#: The functions a case may call: the package's public API.
FUNCTIONS = (
    "is_chord_token",
    "parse_chord",
    "chord_tones",
    "transpose_chord",
    "transposition_table",
    "estimate_key",
    "chord_function",
    "uses_flats",
    "key_name",
)


def _decode(value):
    if isinstance(value, dict) and set(value) == {"tonic", "minor"}:
        return Key(value["tonic"], value["minor"])
    if isinstance(value, list):
        return [_decode(v) for v in value]
    return value


def to_json(value):
    """``value`` in the JSON form cases use (tuples as lists, Key as a dict)."""
    if isinstance(value, Key):
        return {"tonic": value.tonic, "minor": value.minor}
    if isinstance(value, (tuple, list)):
        return [to_json(v) for v in value]
    if isinstance(value, dict):
        return {k: to_json(v) for k, v in value.items()}
    return value


def run_case(case: dict):
    """Call the case's function on its arguments; return the result in JSON form."""
    if case["fn"] not in FUNCTIONS:
        raise ValueError(
            f"Unknown function in case: {case['fn']!r}; one of {FUNCTIONS}"
        )
    func = getattr(chordsym, case["fn"])
    args = [_decode(a) for a in case.get("args", [])]
    kwargs = {k: _decode(v) for k, v in case.get("kwargs", {}).items()}
    return to_json(func(*args, **kwargs))


def load_cases(root: Path | str = ".") -> list[dict]:
    """The cases in ``<root>/fixtures/cases.json``."""
    return json.loads((Path(root) / CASES_PATH).read_text(encoding="utf-8"))["cases"]


def record(root: Path | str = ".") -> Path:
    """Rewrite every case's ``expected`` from the Python implementation; return the path."""
    path = Path(root) / CASES_PATH
    data = json.loads(path.read_text(encoding="utf-8"))
    for case in data["cases"]:
        case["expected"] = run_case(case)
    path.write_text(dumps(data), encoding="utf-8")
    return path


def dumps(data: dict) -> str:
    """The cases file's text: one case per line, so a diff shows exactly which cases changed."""

    def line(obj) -> str:
        return json.dumps(obj, ensure_ascii=False)

    head = {k: v for k, v in data.items() if k != "cases"}
    rows = ",\n".join("  " + line(case) for case in data["cases"])
    fields = "".join(f"\n {line(k)}: {line(v)}," for k, v in head.items())
    return "{" + fields + '\n "cases": [\n' + rows + "\n ]\n}\n"


if __name__ == "__main__":
    print(record())
