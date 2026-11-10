"""Run and record the golden cases in ``fixtures/cases.json``, the behaviour both twins must share.

A case is ``{"fn": <public function name>, "args": [...], "kwargs": {...}, "expected": ...}``
in JSON form:

- tuples are lists; a :class:`~chordsym.Key` is ``{"tonic": int, "minor": bool}``;
- an open mapping in a result (``transposition_table(...)["chords"]``) is a list of
  ``[key, value]`` pairs, because its order is part of the contract and a JSON object's
  is not (JavaScript moves integer-like keys first);
- an exception is ``{"$raises": "ValueError"}`` (TypeScript: ``RangeError``) or
  ``{"$raises": "TypeError"}``;
- ``kwargs`` may only name keyword-only parameters, which the TypeScript twin takes as a
  trailing options object.

The file's ``functions`` list is the public API (``chordsym.__all__`` minus classes); both
test suites check that they cover exactly it. Results are compared as JSON text, so order
matters everywhere.

To add a case, append it with any ``expected`` and run ``python -m chordsym._fixtures``: it
rewrites every ``expected`` from the Python implementation, so review the diff (a changed
expectation is a behaviour change on both sides).

>>> run_case({"fn": "transpose_chord", "args": ["C/E", 3], "kwargs": {"flats": True}})
'Eb/G'
>>> run_case({"fn": "estimate_key", "args": [["Am", "Dm", "E7"]]})
{'tonic': 9, 'minor': True}
>>> run_case({"fn": "key_name", "args": [{"tonic": 12, "minor": False}]})
{'$raises': 'ValueError'}
"""

from __future__ import annotations

import inspect
import json
from pathlib import Path

import chordsym
from chordsym.keys import Key

#: The repository root (where ``fixtures/`` and ``ts/`` live, next to the package).
REPO_ROOT = Path(__file__).resolve().parent.parent

#: The golden cases, relative to the repository root.
CASES_PATH = Path("fixtures") / "cases.json"

#: The exceptions a case may expect; the TypeScript twin throws the mapped JS error.
RAISES = (ValueError, TypeError)


def public_functions() -> tuple[str, ...]:
    """The functions of the public API (``chordsym.__all__``, classes excluded)."""
    return tuple(
        name for name in chordsym.__all__ if inspect.isfunction(getattr(chordsym, name))
    )


#: Per-function result encoders, for results whose JSON form needs more than to_json.
_ENCODERS = {
    "transposition_table": lambda r: {
        **r,
        "chords": [list(kv) for kv in r["chords"].items()],
    },
}


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


def _check_kwargs(name: str, func, kwargs: dict) -> None:
    params = inspect.signature(func).parameters
    for kw in kwargs:
        if kw not in params or params[kw].kind is not inspect.Parameter.KEYWORD_ONLY:
            raise ValueError(
                f"Case for {name}: {kw!r} is not a keyword-only parameter; pass it in args"
            )


def run_case(case: dict):
    """Call the case's function on its arguments; return the result in JSON form."""
    name = case["fn"]
    if name not in public_functions():
        raise ValueError(
            f"Unknown function in case: {name!r}; one of {public_functions()}"
        )
    func = getattr(chordsym, name)
    kwargs = case.get("kwargs", {})
    _check_kwargs(name, func, kwargs)
    try:
        args = [_decode(a) for a in case.get("args", [])]
        result = func(*args, **{k: _decode(v) for k, v in kwargs.items()})
    except RAISES as error:
        return {"$raises": type(error).__name__}
    encoded = to_json(result)
    return _ENCODERS[name](encoded) if name in _ENCODERS else encoded


def same(result, expected) -> bool:
    """Whether two JSON values are equal, order included (what both test suites check)."""
    return json.dumps(result, ensure_ascii=False) == json.dumps(
        expected, ensure_ascii=False
    )


def load(root: Path | str = REPO_ROOT) -> dict:
    """The parsed ``<root>/fixtures/cases.json``."""
    return json.loads((Path(root) / CASES_PATH).read_text(encoding="utf-8"))


def record(root: Path | str = REPO_ROOT) -> Path:
    """Rewrite every case's ``expected`` (and the ``functions`` list) from Python."""
    path = Path(root) / CASES_PATH
    data = load(root)
    data["functions"] = list(public_functions())
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
