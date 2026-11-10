"""What a chord does in a key: estimate a song's key from its chords, label chords by function.

>>> key = estimate_key(["G", "D", "Em", "C", "G", "D", "G"])
>>> key
Key(tonic=7, minor=False)
>>> [chord_function(symbol, key) for symbol in ["G", "Em", "C", "Bb", "N.C."]]
['tonic', 'diatonic', 'diatonic', 'outside', None]
>>> estimate_key(["Am", "Dm", "E7", "Am"])
Key(tonic=9, minor=True)
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass

from chordsym import _grammar
from chordsym.dialects import Dialect, resolve_dialect
from chordsym.parse import parse_chord

_MAJOR_KEY = {degree: set(qs) for degree, qs in _grammar.MAJOR_KEY.items()}
_MINOR_KEY = {degree: set(qs) for degree, qs in _grammar.MINOR_KEY.items()}
_WEIGHTS = _grammar.KEY_WEIGHTS


@dataclass(frozen=True)
class Key:
    """A key: its tonic as a pitch class (C = 0, C# = 1, ... B = 11), major or minor."""

    tonic: int
    minor: bool = False

    def __post_init__(self):
        if isinstance(self.tonic, bool) or not isinstance(self.tonic, int):
            raise TypeError(f"Key tonic must be an int pitch class, not {self.tonic!r}")
        if not 0 <= self.tonic < 12:
            raise ValueError(f"Key tonic must be 0-11 (C = 0), not {self.tonic}")


def _function(parsed: tuple[int, str], key: Key) -> str:
    root, quality = parsed
    degree = (root - key.tonic) % 12
    qualities = (_MINOR_KEY if key.minor else _MAJOR_KEY).get(degree)
    if qualities is None or (quality != "open" and quality not in qualities):
        return "outside"
    return "tonic" if degree == 0 else "diatonic"


def chord_function(
    symbol: str, key: Key, *, dialect: str | Dialect = "default"
) -> str | None:
    """``"tonic"``, ``"diatonic"`` or ``"outside"`` in ``key``; None if ``symbol`` is not a chord.

    ``dialect`` names how ``symbol`` is spelled, as in :func:`chordsym.parse_chord`.
    """
    parsed = parse_chord(symbol, dialect=dialect)
    return None if parsed is None else _function(parsed, key)


def estimate_key(
    symbols: Iterable[str], *, dialect: str | Dialect = "default"
) -> Key | None:
    """The key that best explains a song's chords, in order; None if there are no chords.

    Each chord scores for a key when it belongs to it, and more when it is its
    tonic; a song that starts or ends on a key's tonic chord scores extra for
    that key. Ties go to the major key, and to the lower tonic. ``dialect`` names
    how ``symbols`` are spelled, as in :func:`chordsym.parse_chord`.

    >>> estimate_key(["Cs", "Fs", "Gs", "Cs"], dialect="chordonomicon")
    Key(tonic=1, minor=False)
    """
    normalise = resolve_dialect(
        dialect
    )  # an unknown dialect raises, even with no symbols
    chords = [p for p in (parse_chord(s, dialect=normalise) for s in symbols) if p]
    if not chords:
        return None
    # Each distinct chord is scored once per key, times how often it occurs. That equals
    # adding each occurrence's weight in turn because the weights are integers (exact in
    # floating point in any order; tests/test_chordsym.py checks they stay integers).
    # Still an explicit loop, not sum(), which compensates float rounding on Python 3.12+.
    counts = Counter(chords).items()
    ends = (chords[0], chords[-1])
    best, best_score = None, float("-inf")
    for tonic in range(12):
        for minor in (False, True):
            key = Key(tonic, minor)
            score = 0.0
            for parsed, n in counts:
                score += n * _WEIGHTS[_function(parsed, key)]
            for parsed in ends:
                if _function(parsed, key) == "tonic":
                    score += _WEIGHTS["ends"]
            if score > best_score:
                best, best_score = key, score
    return best
