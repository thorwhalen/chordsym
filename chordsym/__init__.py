"""chordsym: chord symbols without dependencies — parse, pitch classes, keys, transposition.

>>> from chordsym import parse_chord, transpose_chord, estimate_key
>>> parse_chord("Am7"), transpose_chord("Am7", 2), estimate_key(["Am", "Dm", "E7"])
((9, 'minor'), 'Bm7', Key(tonic=9, minor=True))
"""

from chordsym.keys import Key, chord_function, estimate_key
from chordsym.parse import chord_tones, is_chord_token, parse_chord
from chordsym.transpose import (
    key_name,
    transpose_chord,
    transposition_table,
    uses_flats,
)
