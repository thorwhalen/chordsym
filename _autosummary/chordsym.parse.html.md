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

Other spellings are read through a `dialect` (see [`chordsym.dialects`](chordsym.dialects.html.md#module-chordsym.dialects)):

```pycon
>>> parse_chord("Csmin", dialect="chordonomicon"), parse_chord("B:hdim7", dialect="harte")
((1, 'minor'), (11, 'diminished'))
```

### Module Attributes

| [`PARSE_CACHE_SIZE`](#chordsym.parse.PARSE_CACHE_SIZE)   | How many distinct `(symbol, dialect)` results [`parse_chord()`](#chordsym.parse.parse_chord) remembers.   |
|---------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------|

### Functions

| [`chord_tones`](#chordsym.parse.chord_tones)(symbol, \*[, dialect])   | The chord's pitch classes, bass first (the root, or the bass of a slash chord).   |
|---------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| [`is_chord_token`](#chordsym.parse.is_chord_token)(token, \*[, dialect]) | True if `token` reads as a chord symbol (`G`, `F#m7b5`, `E7(#9)`, `C/G`).         |
| [`parse_chord`](#chordsym.parse.parse_chord)(symbol, \*[, dialect])   | `(root pitch class, quality)`, or None for what is not a chord.                   |

### chordsym.parse.PARSE_CACHE_SIZE *= 8192*

How many distinct `(symbol, dialect)` results [`parse_chord()`](#chordsym.parse.parse_chord) remembers.

### chordsym.parse.chord_tones(symbol, , dialect='default')

The chord’s pitch classes, bass first (the root, or the bass of a slash chord).

Triads by quality (`m`, `dim`, `aug`/`+`, `sus2`, `sus4`, `5`), then
sevenths (`7`, `maj7`/`Δ`/`∆`, `dim7`/`o7`, `m7b5`), sixths and added ninths.
`None` for what [`chordsym.parse_chord()`](chordsym.html.md#chordsym.parse_chord) does not read as a chord (in
`dialect`).

```pycon
>>> chord_tones("Co7"), chord_tones("CΔ"), chord_tones("C-Δ7")
((0, 3, 6, 9), (0, 4, 7, 11), (0, 3, 7, 11))
>>> chord_tones("A:min7", dialect="harte"), chord_tones("C:maj/3", dialect="harte")
((9, 0, 4, 7), (4, 0, 7))
```

* **Return type:**
  [`tuple`](https://docs.python.org/3/builtins/stdtypes.html#tuple)[[`int`](https://docs.python.org/3/builtins/functions.html#int), [`...`](https://docs.python.org/3/builtins/constants.html#Ellipsis)] | [`None`](https://docs.python.org/3/builtins/constants.html#None)

### chordsym.parse.is_chord_token(token, , dialect='default')

True if `token` reads as a chord symbol (`G`, `F#m7b5`, `E7(#9)`, `C/G`).

`dialect` is how `token` is spelled: a name in `chordsym.DIALECTS` or a
function into the default spelling (see [`chordsym.dialects`](chordsym.dialects.html.md#module-chordsym.dialects)).

```pycon
>>> is_chord_token("Bb7(4)(9)"), is_chord_token("A7/sus4"), is_chord_token("Bridge")
(True, True, False)
>>> is_chord_token("Gno3d"), is_chord_token("Gno3d", dialect="chordonomicon")
(False, True)
```

* **Return type:**
  [`bool`](https://docs.python.org/3/builtins/functions.html#bool)

### chordsym.parse.parse_chord(symbol, , dialect='default')

`(root pitch class, quality)`, or None for what is not a chord.

The quality is `"major"`, `"minor"`, `"diminished"`, or `"open"` (a
suspended or power chord, which has no third). A bass note is ignored. What
the chart parser would not read as a chord ([`is_chord_token()`](#chordsym.parse.is_chord_token)) is not one.
`dialect` is how `symbol` is spelled: a name in `chordsym.DIALECTS` (the
default reads chart spellings, `"chordonomicon"` and `"harte"` those corpora’s)
or a function into the default spelling (see [`chordsym.dialects`](chordsym.dialects.html.md#module-chordsym.dialects)).

Results are remembered (up to [`PARSE_CACHE_SIZE`](#chordsym.parse.PARSE_CACHE_SIZE)), keyed on the symbol and
the dialect’s function, so a dialect must be pure; results are immutable tuples, so
sharing them is safe.

```pycon
>>> parse_chord("F#m7"), parse_chord("Bbmaj7/D"), parse_chord("A7sus4"), parse_chord("Bm7b5")
((6, 'minor'), (10, 'major'), (9, 'open'), (11, 'diminished'))
>>> parse_chord("C-7"), parse_chord("Bridge"), parse_chord("Co7"), parse_chord("CΔ7")
((0, 'minor'), None, (0, 'diminished'), (0, 'major'))
>>> parse_chord("CmΔ7"), parse_chord("C∆")
((0, 'minor'), (0, 'major'))
>>> parse_chord("A/Cs", dialect="chordonomicon"), parse_chord("N", dialect="harte")
((9, 'major'), None)
```

* **Return type:**
  [`tuple`](https://docs.python.org/3/builtins/stdtypes.html#tuple)[[`int`](https://docs.python.org/3/builtins/functions.html#int), [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)] | [`None`](https://docs.python.org/3/builtins/constants.html#None)
