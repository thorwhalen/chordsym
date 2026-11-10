"""Move chord symbols by semitones, spelled for the target key.

>>> transpose_chord("F#m7", 1), transpose_chord("C/E", 3, flats=True)
('Gm7', 'Eb/G')
>>> transposition_table(["G", "D", "Em", "C", "G"], 3)
{'semitones': 3, 'key': 'Bb', 'chords': {'G': 'Bb', 'D': 'F', 'Em': 'Gm', 'C': 'Eb'}}
"""

from __future__ import annotations

from collections.abc import Iterable

from chordsym import _grammar
from chordsym.keys import Key, estimate_key
from chordsym.parse import _ACCIDENTALS, _PITCH_CLASSES, _compile, parse_chord

_SHARP_NAMES = _grammar.SHARP_NAMES
_FLAT_NAMES = _grammar.FLAT_NAMES
_FLAT_MAJOR_TONICS = frozenset(_grammar.FLAT_MAJOR_TONICS)
_FLAT_MINOR_TONICS = frozenset(_grammar.FLAT_MINOR_TONICS)
#: Groups: lead, root, rest, bass, tail.
_TRANSPOSABLE_RE = _compile("transposable")


def _pitch_class(name: str) -> int:
    return (_PITCH_CLASSES[name[0]] + _ACCIDENTALS[name[1:]]) % 12


def uses_flats(key: Key | None) -> bool:
    """Whether chords in ``key`` are spelled with flats (Bb, Eb) rather than sharps.

    >>> uses_flats(Key(5)), uses_flats(Key(7)), uses_flats(Key(2, minor=True)), uses_flats(None)
    (True, False, True, False)
    """
    if key is None:
        return False
    return key.tonic in (_FLAT_MINOR_TONICS if key.minor else _FLAT_MAJOR_TONICS)


def key_name(key: Key, *, flats: bool | None = None) -> str:
    """``"G"``, ``"Bb"``, ``"F#m"``: the key spelled as its tonic chord.

    >>> key_name(Key(10)), key_name(Key(6, minor=True)), key_name(Key(6, minor=True), flats=True)
    ('Bb', 'F#m', 'Gbm')
    """
    flats = uses_flats(key) if flats is None else flats
    return (_FLAT_NAMES if flats else _SHARP_NAMES)[key.tonic] + (
        "m" if key.minor else ""
    )


def transpose_chord(symbol: str, semitones: int, *, flats: bool = False) -> str:
    """``symbol`` moved by ``semitones``: root and bass move, the rest is kept as written.

    ``flats`` spells moved notes with flats (choose it from the target key with
    :func:`uses_flats`). What is not a chord comes back unchanged.

    >>> transpose_chord("G", 2), transpose_chord("F#m7", 1), transpose_chord("C/E", 3, flats=True)
    ('A', 'Gm7', 'Eb/G')
    >>> transpose_chord("Bbmaj7", -1, flats=True), transpose_chord("N.C.", 4), transpose_chord("Am", 0)
    ('Amaj7', 'N.C.', 'Am')
    >>> [transpose_chord(c, 2) for c in ("D7/9", "Bm5-/7", "C6/9", "C(4/9)", "(Em7)", "Am7/G)")]
    ['E7/9', 'C#m5-/7', 'D6/9', 'D(4/9)', '(F#m7)', 'Bm7/A)']
    """
    if semitones % 12 == 0 or parse_chord(symbol) is None:
        return symbol
    match = _TRANSPOSABLE_RE.fullmatch(symbol)
    if match is None:
        return symbol
    names = _FLAT_NAMES if flats else _SHARP_NAMES

    def moved(name: str) -> str:
        return names[(_pitch_class(name) + semitones) % 12]

    lead, root, rest, bass, tail = match.groups()
    out = lead + moved(root) + rest
    if bass:
        out += "/" + moved(bass) + (tail or "")
    return out


def transposition_table(
    symbols: Iterable[str], semitones: int, *, key: Key | None = None
) -> dict:
    """The chords of a song moved by ``semitones``, spelled for the new key.

    ``symbols`` are the song's chords in order (they give the key when ``key`` is
    not given). Returns ``{"semitones", "key", "chords"}``: the new key's name
    (``""`` when there are no chords) and ``{original: transposed}`` over the
    distinct chords, in order of first appearance.

    >>> transposition_table(["G", "D", "Em", "C", "G"], 3)
    {'semitones': 3, 'key': 'Bb', 'chords': {'G': 'Bb', 'D': 'F', 'Em': 'Gm', 'C': 'Eb'}}
    """
    symbols = list(symbols)
    key = key or estimate_key(symbols)
    target = Key((key.tonic + semitones) % 12, key.minor) if key else None
    flats = uses_flats(target)
    chords = {
        symbol: transpose_chord(symbol, semitones, flats=flats)
        for symbol in dict.fromkeys(symbols)
    }
    return {
        "semitones": semitones,
        "key": key_name(target) if target else "",
        "chords": chords,
    }
