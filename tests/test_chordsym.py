"""Tests for chordsym."""

import random

import pytest

from chordsym import (
    DIALECTS,
    Key,
    chord_function,
    chord_tones,
    estimate_key,
    is_chord_token,
    key_name,
    parse_chord,
    transpose_chord,
    transposition_table,
    uses_flats,
)
from chordsym import _grammar
from chordsym._fixtures import load
from chordsym.keys import _function
from chordsym.parse import PARSE_CACHE_SIZE, _parse


def test_parse_and_tokens():
    assert parse_chord("Bm7b5") == (11, "diminished")
    assert parse_chord("A7sus4") == (9, "open")
    assert parse_chord("Bridge") is None and not is_chord_token("Bridge")
    assert is_chord_token("Bb7(4)(9)")


def test_tones():
    assert chord_tones("Am/G") == (7, 9, 0, 4)
    assert chord_tones("N.C.") is None


def test_keys():
    assert estimate_key([]) is None
    assert estimate_key(["Am", "Dm", "E7", "Am"]) == Key(9, minor=True)
    assert chord_function("Bb", Key(7)) == "outside"
    assert uses_flats(Key(5)) and not uses_flats(None)
    assert key_name(Key(6, minor=True)) == "F#m"


def test_transpose_roundtrip():
    for c in ("G", "F#m7", "C/E", "D7/9", "C6/9", "(Em7)"):
        assert transpose_chord(transpose_chord(c, 5), -5, flats=False) in (
            c,
            transpose_chord(transpose_chord(c, 5), -5),
        )
    assert transpose_chord("N.C.", 4) == "N.C."
    assert transposition_table(["G", "D"], 0)["chords"] == {"G": "G", "D": "D"}


def test_dialects():
    assert parse_chord("Cs") is None and parse_chord("Cs", dialect="chordonomicon") == (
        1,
        "major",
    )
    assert chord_tones("Gno3d", dialect="chordonomicon") == (7, 2)
    assert parse_chord("A:min", dialect="harte") == (9, "minor")
    assert parse_chord("N", dialect="harte") is None
    with pytest.raises(ValueError, match="chordonomicon"):
        parse_chord("C", dialect="nope")


def test_dialects_are_extensible():
    DIALECTS["lower"] = str.capitalize
    try:
        assert parse_chord("am", dialect="lower") == (9, "minor")
        assert estimate_key(["am", "dm", "e7"], dialect="lower") == Key(9, minor=True)
    finally:
        del DIALECTS["lower"]


def test_parse_chord_is_memoised_on_symbol_and_dialect():
    assert _parse.cache_info().maxsize == PARSE_CACHE_SIZE
    _parse.cache_clear()
    first = parse_chord("Cs", dialect="chordonomicon")
    assert parse_chord("Cs", dialect="chordonomicon") is first  # a cache hit
    assert parse_chord("Cs") is None  # the dialect is part of the key
    assert isinstance(first, tuple)  # immutable, so sharing the cached value is safe
    assert _parse.cache_info().hits == 1


def _estimate_key_per_chord(symbols):
    """estimate_key as it was before counting chords: every occurrence summed in turn."""
    chords = [p for p in map(parse_chord, symbols) if p]
    if not chords:
        return None
    best, best_score = None, float("-inf")
    for tonic in range(12):
        for minor in (False, True):
            key, score = Key(tonic, minor), 0.0
            for parsed in chords:
                score += _grammar.KEY_WEIGHTS[_function(parsed, key)]
            for parsed in (chords[0], chords[-1]):
                if _function(parsed, key) == "tonic":
                    score += _grammar.KEY_WEIGHTS["ends"]
            if score > best_score:
                best, best_score = key, score
    return best


def test_counted_key_scores_are_exact():
    """Scoring distinct chords times their count equals the per-chord sum only because
    the weights are integers (exact in floating point whatever the order)."""
    assert all(float(w).is_integer() for w in _grammar.KEY_WEIGHTS.values())
    tokens = [c["args"][0] for c in load()["cases"] if c["fn"] == "parse_chord"]
    rng = random.Random(0)
    songs = [
        [rng.choice(tokens) for _ in range(rng.randint(0, 80))] for _ in range(2000)
    ]
    songs += [c["args"][0] for c in load()["cases"] if c["fn"] == "estimate_key"]
    for song in songs:
        if all(isinstance(t, str) for t in song):
            assert estimate_key(song) == _estimate_key_per_chord(song), song
