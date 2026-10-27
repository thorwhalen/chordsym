"""Tests for chordsym."""

from chordsym import (
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
