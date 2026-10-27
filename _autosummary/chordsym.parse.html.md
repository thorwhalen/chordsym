# chordsym.parse

Read a chord symbol: is it one, what is its root and quality, which pitch classes it sounds.

Pure standard library. A pitch class is an int 0-11 (C = 0, C# = 1, … B = 11).

```pycon
>>> is_chord_token("F#m7b5"), is_chord_token("Bridge")
(True, False)
>>> parse_chord("Bbmaj7/D")
(10, 'major')
>>> chord_tones("Cmaj7"), chord_tones("Am/G"), chord_tones("F#m7b5")
((0, 4, 7, 11), (7, 9, 0, 4), (6, 9, 0, 4))
```

### Functions

| [`chord_tones`](#chordsym.parse.chord_tones)(symbol)   | The chord's pitch classes, bass first (the root, or the bass of a slash chord).   |
|------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| [`is_chord_token`](#chordsym.parse.is_chord_token)(token) | True if `token` reads as a chord symbol (`G`, `F#m7b5`, `E7(#9)`, `C/G`).         |
| [`parse_chord`](#chordsym.parse.parse_chord)(symbol)   | `(root pitch class, quality)`, or None for what is not a chord.                   |

### chordsym.parse.chord_tones(symbol)

The chord’s pitch classes, bass first (the root, or the bass of a slash chord).

Triads by quality (`m`, `dim`, `aug`/`+`, `sus2`, `sus4`, `5`), then
sevenths (`7`, `maj7`, `dim7`, `m7b5`), sixths and added ninths. `None`
for what `chordsym.parse_chord()` does not read as a chord.

* **Return type:**
  [`tuple`](https://docs.python.org/3/builtins/stdtypes.html#tuple)[[`int`](https://docs.python.org/3/builtins/functions.html#int), [`...`](https://docs.python.org/3/builtins/constants.html#Ellipsis)] | [`None`](https://docs.python.org/3/builtins/constants.html#None)

### chordsym.parse.is_chord_token(token)

True if `token` reads as a chord symbol (`G`, `F#m7b5`, `E7(#9)`, `C/G`).

```pycon
>>> is_chord_token("Bb7(4)(9)"), is_chord_token("A7/sus4"), is_chord_token("Bridge")
(True, True, False)
```

* **Return type:**
  [`bool`](https://docs.python.org/3/builtins/functions.html#bool)

### chordsym.parse.parse_chord(symbol)

`(root pitch class, quality)`, or None for what is not a chord.

The quality is `"major"`, `"minor"`, `"diminished"`, or `"open"` (a
suspended or power chord, which has no third). A bass note is ignored. What
the chart parser would not read as a chord ([`is_chord_token()`](#chordsym.parse.is_chord_token)) is not one.

```pycon
>>> parse_chord("F#m7"), parse_chord("Bbmaj7/D"), parse_chord("A7sus4"), parse_chord("Bm7b5")
((6, 'minor'), (10, 'major'), (9, 'open'), (11, 'diminished'))
>>> parse_chord("C-7"), parse_chord("Bridge")
((0, 'minor'), None)
```

* **Return type:**
  [`tuple`](https://docs.python.org/3/builtins/stdtypes.html#tuple)[[`int`](https://docs.python.org/3/builtins/functions.html#int), [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)] | [`None`](https://docs.python.org/3/builtins/constants.html#None)
