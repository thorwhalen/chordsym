"""The shared grammar stays portable to JavaScript, and the TS twin's generated copy stays current."""

import re
import sys
from pathlib import Path

import pytest

from chordsym import _grammar
from chordsym._codegen import (
    TS_GRAMMAR_PATH,
    grammar_names,
    render_ts,
    whitespace_code_points,
)

ROOT = Path(__file__).resolve().parent.parent

#: Escapes whose meaning differs between Python ``re`` and JavaScript ``RegExp``, or that
#: JavaScript lacks.
_NON_PORTABLE_ESCAPES = set("dDwWsSbBAZ")


def _portability_problems(source: str, flags: str) -> list[str]:
    """What in ``source`` would match differently in Python and in JS (``u`` flag)."""
    problems, i, in_class = [], 0, False
    while i < len(source):
        char = source[i]
        if char == "\\":
            escaped = source[i + 1 : i + 2]
            if escaped in _NON_PORTABLE_ESCAPES and not (in_class and escaped == "b"):
                problems.append(f"\\{escaped} at {i}")
            i += 2
            continue
        if in_class:
            in_class = char != "]"
        elif char == "[":
            in_class = True
        elif char == "." and "s" not in flags:
            problems.append(
                f"'.' without the s flag at {i} (JS also excludes \\r, \\u2028)"
            )
        elif char == "$":
            problems.append(f"'$' at {i} (Python also matches before a final newline)")
        i += 1
    return problems


@pytest.mark.parametrize("name", sorted(_grammar.PATTERNS))
def test_pattern_is_portable(name):
    source, flags = _grammar.PATTERNS[name]
    assert _portability_problems(source, flags) == []
    assert set(flags) <= {"s"}
    re.compile(source)


_REWRITES = [
    (name, i, source)
    for name, rules in _grammar.DIALECT_REWRITES.items()
    for i, (source, _) in enumerate(rules)
]


@pytest.mark.parametrize("name, i, source", _REWRITES)
def test_dialect_rewrite_is_portable(name, i, source):
    """Dialect rewrites run with the ``g`` and ``u`` flags in JS: portable, never empty."""
    assert _portability_problems(source, "") == []
    pattern = re.compile(source)
    assert all(
        len(m.group()) > 0
        for text in ("", "C", "Cs", "Gno3d", "Asus4/Cs", "Emajs9")
        for m in pattern.finditer(text)
    )


@pytest.mark.parametrize(
    "source, flags, bad",
    [
        (r"\d", "", True),
        (r"\\d", "", False),
        (r"\\\d", "", True),
        (r"[\b]", "", False),
        (r"a.b", "", True),
        (r"a.b", "s", False),
        (r"[.]", "", False),
        (r"a$", "", True),
        (r"\$", "", False),
    ],
)
def test_portability_lint(source, flags, bad):
    assert bool(_portability_problems(source, flags)) is bad


def test_ws_is_exactly_python_whitespace():
    ws = re.compile(f"[{_grammar.WS}]")
    matched = [c for c in range(sys.maxunicode + 1) if ws.fullmatch(chr(c))]
    assert matched == whitespace_code_points()


def test_every_grammar_name_is_generated():
    ts = render_ts()
    for name in grammar_names() + ["WHITESPACE"]:
        assert f"export const {name} = " in ts


@pytest.mark.skipif(not (ROOT / "ts").exists(), reason="no TypeScript twin here")
def test_generated_ts_grammar_is_current():
    committed = (ROOT / TS_GRAMMAR_PATH).read_text(encoding="utf-8")
    assert committed == render_ts(), "run: python -m chordsym._codegen"


@pytest.mark.skipif(not (ROOT / "ts").exists(), reason="no TypeScript twin here")
def test_npm_package_carries_the_license():
    assert (ROOT / "ts" / "LICENSE").read_text() == (ROOT / "LICENSE").read_text()
