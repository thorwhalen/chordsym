"""chordsym: chord symbols without dependencies — parse, pitch classes, keys, transposition.

>>> from chordsym import parse_chord, transpose_chord, estimate_key
>>> parse_chord("Am7"), transpose_chord("Am7", 2), estimate_key(["Am", "Dm", "E7"])
((9, 'minor'), 'Bm7', Key(tonic=9, minor=True))
>>> parse_chord("Fsmin", dialect="chordonomicon"), parse_chord("C:maj7", dialect="harte")
((6, 'minor'), (0, 'major'))
"""

from chordsym.keys import Key, chord_function, estimate_key
from chordsym.parse import DIALECTS, chord_tones, is_chord_token, parse_chord
from chordsym.transpose import (
    key_name,
    transpose_chord,
    transposition_table,
    uses_flats,
)

__all__ = [
    "DIALECTS",
    "Key",
    "chord_function",
    "chord_tones",
    "estimate_key",
    "is_chord_token",
    "key_name",
    "parse_chord",
    "transpose_chord",
    "transposition_table",
    "uses_flats",
]
