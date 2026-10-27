# chordsym.transpose

Move chord symbols by semitones, spelled for the target key.

```pycon
>>> transpose_chord("F#m7", 1), transpose_chord("C/E", 3, flats=True)
('Gm7', 'Eb/G')
>>> transposition_table(["G", "D", "Em", "C", "G"], 3)
{'semitones': 3, 'key': 'Bb', 'chords': {'G': 'Bb', 'D': 'F', 'Em': 'Gm', 'C': 'Eb'}}
```

### Functions

| [`key_name`](#chordsym.transpose.key_name)(key, \*[, flats])                         | `"G"`, `"Bb"`, `"F#m"`: the key spelled as its tonic chord.                     |
|-----------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------|
| [`transpose_chord`](#chordsym.transpose.transpose_chord)(symbol, semitones, \*[, flats])    | `symbol` moved by `semitones`: root and bass move, the rest is kept as written. |
| [`transposition_table`](#chordsym.transpose.transposition_table)(symbols, semitones, \*[, key]) | The chords of a song moved by `semitones`, spelled for the new key.             |
| [`uses_flats`](#chordsym.transpose.uses_flats)(key)                                    | Whether chords in `key` are spelled with flats (Bb, Eb) rather than sharps.     |

### chordsym.transpose.key_name(key, , flats=None)

`"G"`, `"Bb"`, `"F#m"`: the key spelled as its tonic chord.

```pycon
>>> key_name(Key(10)), key_name(Key(6, minor=True)), key_name(Key(6, minor=True), flats=True)
('Bb', 'F#m', 'Gbm')
```

* **Return type:**
  [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

### chordsym.transpose.transpose_chord(symbol, semitones, , flats=False)

`symbol` moved by `semitones`: root and bass move, the rest is kept as written.

`flats` spells moved notes with flats (choose it from the target key with
[`uses_flats()`](#chordsym.transpose.uses_flats)). What is not a chord comes back unchanged.

```pycon
>>> transpose_chord("G", 2), transpose_chord("F#m7", 1), transpose_chord("C/E", 3, flats=True)
('A', 'Gm7', 'Eb/G')
>>> transpose_chord("Bbmaj7", -1, flats=True), transpose_chord("N.C.", 4), transpose_chord("Am", 0)
('Amaj7', 'N.C.', 'Am')
>>> [transpose_chord(c, 2) for c in ("D7/9", "Bm5-/7", "C6/9", "C(4/9)", "(Em7)", "Am7/G)")]
['E7/9', 'C#m5-/7', 'D6/9', 'D(4/9)', '(F#m7)', 'Bm7/A)']
```

* **Return type:**
  [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

### chordsym.transpose.transposition_table(symbols, semitones, , key=None)

The chords of a song moved by `semitones`, spelled for the new key.

`symbols` are the song’s chords in order (they give the key when `key` is
not given). Returns `{"semitones", "key", "chords"}`: the new key’s name
(`""` when there are no chords) and `{original: transposed}` over the
distinct chords, in order of first appearance.

```pycon
>>> transposition_table(["G", "D", "Em", "C", "G"], 3)
{'semitones': 3, 'key': 'Bb', 'chords': {'G': 'Bb', 'D': 'F', 'Em': 'Gm', 'C': 'Eb'}}
```

* **Return type:**
  [`dict`](https://docs.python.org/3/builtins/stdtypes.html#dict)

### chordsym.transpose.uses_flats(key)

Whether chords in `key` are spelled with flats (Bb, Eb) rather than sharps.

```pycon
>>> uses_flats(Key(5)), uses_flats(Key(7)), uses_flats(Key(2, minor=True)), uses_flats(None)
(True, False, True, False)
```

* **Return type:**
  [`bool`](https://docs.python.org/3/builtins/functions.html#bool)
