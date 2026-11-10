"""The shared grammar stays portable to JavaScript, and the TS twin's generated copy stays current."""

import re
import sys
from pathlib import Path

import pytest

from chordsym import _grammar
from chordsym._codegen import TS_GRAMMAR_PATH, render_ts

ROOT = Path(__file__).resolve().parent.parent

#: Escapes whose meaning differs between Python ``re`` and JavaScript ``RegExp``.
_NON_PORTABLE = re.compile(r"(?<!\\)(?:\\\\)*\\[dDwWsSbB]")


@pytest.mark.parametrize("name", sorted(_grammar.PATTERNS))
def test_pattern_is_portable(name):
    source, flags = _grammar.PATTERNS[name]
    assert not _NON_PORTABLE.search(source), (
        f"{name}: use [0-9] / WS, not \\d \\w \\s \\b"
    )
    assert set(flags) <= {"s"}
    re.compile(source)


def test_ws_is_exactly_python_whitespace():
    ws = re.compile(f"[{_grammar.WS}]")
    spaces = {chr(c) for c in range(sys.maxunicode + 1) if chr(c).isspace()}
    matched = {chr(c) for c in range(sys.maxunicode + 1) if ws.fullmatch(chr(c))}
    assert matched == spaces


@pytest.mark.skipif(not (ROOT / "ts").exists(), reason="no TypeScript twin here")
def test_generated_ts_grammar_is_current():
    committed = (ROOT / TS_GRAMMAR_PATH).read_text(encoding="utf-8")
    assert committed == render_ts(), "run: python -m chordsym._codegen"
