# chordsym

chordsym: chord symbols without dependencies — parse, pitch classes, keys, transposition.

```pycon
>>> from chordsym import parse_chord, transpose_chord, estimate_key
>>> parse_chord("Am7"), transpose_chord("Am7", 2), estimate_key(["Am", "Dm", "E7"])
((9, 'minor'), 'Bm7', Key(tonic=9, minor=True))
```

### Functions

| [`chord_function`](#chordsym.chord_function)(symbol, key)                        | `"tonic"`, `"diatonic"` or `"outside"` in `key`; None if `symbol` is not a chord.   |
|-----------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------|
| [`chord_tones`](#chordsym.chord_tones)(symbol)                                | The chord's pitch classes, bass first (the root, or the bass of a slash chord).     |
| [`estimate_key`](#chordsym.estimate_key)(symbols)                              | The key that best explains a song's chords, in order; None if there are no chords.  |
| [`is_chord_token`](#chordsym.is_chord_token)(token)                              | True if `token` reads as a chord symbol (`G`, `F#m7b5`, `E7(#9)`, `C/G`).           |
| [`key_name`](#chordsym.key_name)(key, \*[, flats])                         | `"G"`, `"Bb"`, `"F#m"`: the key spelled as its tonic chord.                         |
| [`parse_chord`](#chordsym.parse_chord)(symbol)                                | `(root pitch class, quality)`, or None for what is not a chord.                     |
| [`transpose_chord`](#chordsym.transpose_chord)(symbol, semitones, \*[, flats])    | `symbol` moved by `semitones`: root and bass move, the rest is kept as written.     |
| [`transposition_table`](#chordsym.transposition_table)(symbols, semitones, \*[, key]) | The chords of a song moved by `semitones`, spelled for the new key.                 |
| [`uses_flats`](#chordsym.uses_flats)(key)                                    | Whether chords in `key` are spelled with flats (Bb, Eb) rather than sharps.         |

### Classes

| [`Key`](#chordsym.Key)(tonic[, minor])   | A key: its tonic as a pitch class (C = 0, C# = 1, .   |
|------------------------------------------------------------------------|-------------------------------------------------------|

### *class* chordsym.Key(tonic, minor=False)

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

A key: its tonic as a pitch class (C = 0, C# = 1, … B = 11), major or minor.

### chordsym.chord_function(symbol, key)

`"tonic"`, `"diatonic"` or `"outside"` in `key`; None if `symbol` is not a chord.

* **Return type:**
  [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None)

### chordsym.chord_tones(symbol)

The chord’s pitch classes, bass first (the root, or the bass of a slash chord).

Triads by quality (`m`, `dim`, `aug`/`+`, `sus2`, `sus4`, `5`), then
sevenths (`7`, `maj7`, `dim7`, `m7b5`), sixths and added ninths. `None`
for what [`chordsym.parse_chord()`](#chordsym.parse_chord) does not read as a chord.

* **Return type:**
  [`tuple`](https://docs.python.org/3/builtins/stdtypes.html#tuple)[[`int`](https://docs.python.org/3/builtins/functions.html#int), [`...`](https://docs.python.org/3/builtins/constants.html#Ellipsis)] | [`None`](https://docs.python.org/3/builtins/constants.html#None)

### chordsym.estimate_key(symbols)

The key that best explains a song’s chords, in order; None if there are no chords.

Each chord scores for a key when it belongs to it, and more when it is its
tonic; a song that starts or ends on a key’s tonic chord scores extra for
that key. Ties go to the major key, and to the lower tonic.

* **Return type:**
  [`Key`](chordsym.keys.html.md#chordsym.keys.Key) | [`None`](https://docs.python.org/3/builtins/constants.html#None)

### chordsym.is_chord_token(token)

True if `token` reads as a chord symbol (`G`, `F#m7b5`, `E7(#9)`, `C/G`).

```pycon
>>> is_chord_token("Bb7(4)(9)"), is_chord_token("A7/sus4"), is_chord_token("Bridge")
(True, True, False)
```

* **Return type:**
  [`bool`](https://docs.python.org/3/builtins/functions.html#bool)

### chordsym.key_name(key, , flats=None)

`"G"`, `"Bb"`, `"F#m"`: the key spelled as its tonic chord.

```pycon
>>> key_name(Key(10)), key_name(Key(6, minor=True)), key_name(Key(6, minor=True), flats=True)
('Bb', 'F#m', 'Gbm')
```

* **Return type:**
  [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

### chordsym.parse_chord(symbol)

`(root pitch class, quality)`, or None for what is not a chord.

The quality is `"major"`, `"minor"`, `"diminished"`, or `"open"` (a
suspended or power chord, which has no third). A bass note is ignored. What
the chart parser would not read as a chord ([`is_chord_token()`](#chordsym.is_chord_token)) is not one.

```pycon
>>> parse_chord("F#m7"), parse_chord("Bbmaj7/D"), parse_chord("A7sus4"), parse_chord("Bm7b5")
((6, 'minor'), (10, 'major'), (9, 'open'), (11, 'diminished'))
>>> parse_chord("C-7"), parse_chord("Bridge")
((0, 'minor'), None)
```

* **Return type:**
  [`tuple`](https://docs.python.org/3/builtins/stdtypes.html#tuple)[[`int`](https://docs.python.org/3/builtins/functions.html#int), [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)] | [`None`](https://docs.python.org/3/builtins/constants.html#None)

### chordsym.transpose_chord(symbol, semitones, , flats=False)

`symbol` moved by `semitones`: root and bass move, the rest is kept as written.

`flats` spells moved notes with flats (choose it from the target key with
[`uses_flats()`](#chordsym.uses_flats)). What is not a chord comes back unchanged.

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

### chordsym.transposition_table(symbols, semitones, , key=None)

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

### chordsym.uses_flats(key)

Whether chords in `key` are spelled with flats (Bb, Eb) rather than sharps.

```pycon
>>> uses_flats(Key(5)), uses_flats(Key(7)), uses_flats(Key(2, minor=True)), uses_flats(None)
(True, False, True, False)
```

* **Return type:**
  [`bool`](https://docs.python.org/3/builtins/functions.html#bool)

### Modules

| [`keys`](chordsym.keys.html.md#module-chordsym.keys)           | What a chord does in a key: estimate a song's key from its chords, label chords by function.   |
|--------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------|
| [`parse`](chordsym.parse.html.md#module-chordsym.parse)         | Read a chord symbol: is it one, what is its root and quality, which pitch classes it sounds.   |
| [`transpose`](chordsym.transpose.html.md#module-chordsym.transpose) | Move chord symbols by semitones, spelled for the target key.                                   |
