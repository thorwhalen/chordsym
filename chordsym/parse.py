"""Read a chord symbol: is it one, what is its root and quality, which pitch classes it sounds.

Pure standard library. A pitch class is an int 0-11 (C = 0, C# = 1, ... B = 11).

>>> is_chord_token("F#m7b5"), is_chord_token("Bridge")
(True, False)
>>> parse_chord("Bbmaj7/D")
(10, 'major')
>>> chord_tones("Cmaj7"), chord_tones("Am/G"), chord_tones("F#m7b5")
((0, 4, 7, 11), (7, 9, 0, 4), (6, 9, 0, 4))
"""

from __future__ import annotations

import re

from chordsym import _grammar


def _compile(name: str) -> re.Pattern:
    source, flags = _grammar.PATTERNS[name]
    return re.compile(source, re.DOTALL if "s" in flags else 0)


_CHORD_RE = _compile("chord")
_ROOT_RE = _compile("root")
_DIMINISHED_RE = _compile("diminished")
_POWER_RE = _compile("power")
_NOTE_RE = _compile("note")
_MAJOR_SEVENTH_RE = _compile("major_seventh")
_SEVENTH_RE = _compile("seventh")
_SIXTH_RE = _compile("sixth")
_NINTH_RE = _compile("ninth")
_PITCH_CLASSES = _grammar.PITCH_CLASSES
_ACCIDENTALS = _grammar.ACCIDENTALS


def is_chord_token(token: str) -> bool:
    """True if ``token`` reads as a chord symbol (``G``, ``F#m7b5``, ``E7(#9)``, ``C/G``).

    >>> is_chord_token("Bb7(4)(9)"), is_chord_token("A7/sus4"), is_chord_token("Bridge")
    (True, True, False)
    """
    return bool(_CHORD_RE.fullmatch(token))


def parse_chord(symbol: str) -> tuple[int, str] | None:
    """``(root pitch class, quality)``, or None for what is not a chord.

    The quality is ``"major"``, ``"minor"``, ``"diminished"``, or ``"open"`` (a
    suspended or power chord, which has no third). A bass note is ignored. What
    the chart parser would not read as a chord (:func:`is_chord_token`) is not one.

    >>> parse_chord("F#m7"), parse_chord("Bbmaj7/D"), parse_chord("A7sus4"), parse_chord("Bm7b5")
    ((6, 'minor'), (10, 'major'), (9, 'open'), (11, 'diminished'))
    >>> parse_chord("C-7"), parse_chord("Bridge")
    ((0, 'minor'), None)
    """
    symbol = symbol.strip()
    match = _ROOT_RE.fullmatch(symbol)
    if not (match and is_chord_token(symbol)):
        return None
    letter, accidental, rest = match.groups()
    root = (_PITCH_CLASSES[letter] + _ACCIDENTALS[accidental]) % 12
    if rest.startswith(("maj", "M")):
        quality = "major"
    elif _DIMINISHED_RE.match(rest):
        quality = "diminished"
    elif rest.startswith(("min", "m", "-")):  # "C-7" is jazz for Cm7
        quality = "minor"
    elif "sus" in rest or _POWER_RE.match(rest):
        quality = "open"
    else:
        quality = "major"
    return root, quality


def _note(text: str) -> int | None:
    m = _NOTE_RE.match(text.strip())
    if not m:
        return None
    return (_PITCH_CLASSES[m.group(1)] + _ACCIDENTALS[m.group(2)]) % 12


def chord_tones(symbol: str) -> tuple[int, ...] | None:
    """The chord's pitch classes, bass first (the root, or the bass of a slash chord).

    Triads by quality (``m``, ``dim``, ``aug``/``+``, ``sus2``, ``sus4``, ``5``), then
    sevenths (``7``, ``maj7``, ``dim7``, ``m7b5``), sixths and added ninths. ``None``
    for what :func:`chordsym.parse_chord` does not read as a chord.
    """
    parsed = parse_chord(symbol)
    if parsed is None:
        return None
    root, quality = parsed
    head, _, bass_text = symbol.strip().partition("/")
    rest = _NOTE_RE.sub("", head, count=1)
    third = {"minor": 3, "diminished": 3}.get(quality, 4)
    fifth = 6 if quality == "diminished" else 7
    if "aug" in rest or rest.startswith("+"):
        fifth = 8
    intervals = [0, third, fifth]
    if quality == "open":  # suspended or power: no third
        intervals = (
            [0, 7] if _POWER_RE.match(rest) else [0, 2 if "sus2" in rest else 5, 7]
        )
    if "dim7" in rest or rest in ("°7", "o7"):
        intervals.append(9)
    elif _MAJOR_SEVENTH_RE.search(rest):
        intervals.append(11)
    elif _SEVENTH_RE.search(rest):
        intervals.append(10)
    if _SIXTH_RE.search(rest):
        intervals.append(9)
    if _NINTH_RE.search(rest) and 2 not in intervals:
        intervals.append(2)
    tones = list(dict.fromkeys((root + i) % 12 for i in intervals))
    bass = _note(bass_text) if bass_text else None
    if bass is not None:
        tones = [bass] + [t for t in tones if t != bass]
    return tuple(tones)
