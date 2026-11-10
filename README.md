# chordsym

Chord symbols without dependencies (standard library only): is this token a chord, which root and quality, which pitch classes, which key does a song's chord list suggest, and how do the chords read moved by N semitones.

```python
>>> from chordsym import parse_chord, chord_tones, transpose_chord, transposition_table, estimate_key
>>> parse_chord("F#m7"), chord_tones("Cmaj7")
((6, 'minor'), (0, 4, 7, 11))
>>> transpose_chord("C/E", 3, flats=True)
'Eb/G'
>>> transposition_table(["G", "D", "Em", "C"], 3)["chords"]
{'G': 'Bb', 'D': 'F', 'Em': 'Gm', 'C': 'Eb'}
```

It reads the spellings found in scraped chord charts (`C6/9`, `Bm5-/7`, Brazilian `7M`, `E7(#9)`, `D/F#`, `Co7`, `CΔ7`), not only textbook ones. Pitch classes are ints 0-11 (C = 0).

Other spellings are read through a `dialect=` keyword (on `parse_chord`, `chord_tones`, `is_chord_token`, `chord_function` and `estimate_key`), which rewrites a symbol into the default spelling first; `chordsym.DIALECTS` maps each name to its function, and a new entry adds a dialect:

- `"default"`: the chart spellings above.
- `"chordonomicon"`: the Chordonomicon corpus, sharps written `s` (`Cs`, `Fsmin`, `A/Cs`) and power chords `no3d` (`Gno3d` is `G5`).
- `"harte"`: Harte's `root:shorthand` (`C:maj7`, `A:min`, `B:hdim7`, `G:(1,5)`); a degree bass (`C:maj/3`) is ignored, and `N` (no chord) is not a chord.

```python
>>> parse_chord("Fsmin", dialect="chordonomicon"), chord_tones("B:hdim7", dialect="harte")
((6, 'minor'), (11, 2, 5, 9))
```

## In the browser: the TypeScript twin

The same functions ship to npm as `chordsym` (in `ts/`), with camelCase names and keyword arguments as an options object:

```ts
import { parseChord, transposeChord, estimateKey } from "chordsym";

parseChord("Am7");                         // [9, "minor"]
transposeChord("C/E", 3, { flats: true }); // "Eb/G"
estimateKey(["Am", "Dm", "E7"]);           // { tonic: 9, minor: true }
```

The two are kept identical by construction, not by care:

- **One grammar.** Every regular expression and table lives in `chordsym/_grammar.py`, written in the subset of regex syntax that means the same in Python and JavaScript (no `\d`, `\s`, `\w`, `\b`). `python -m chordsym._codegen` writes it to `ts/src/grammar.generated.ts`, and a test fails if that file is stale.
- **One set of golden cases.** `fixtures/cases.json` holds about 1,500 calls with their expected results, errors included (`ValueError` in Python is `RangeError` in TypeScript). pytest and vitest both run every one and compare them as JSON text, so order matters. To add a case, append it and run `python -m chordsym._fixtures`, which records the Python results; review the diff, since a changed expectation is a behaviour change on both sides.
- **A wide net before releases.** `python scripts/twin_differential.py` (after `cd ts && npm run build`) runs about 75,000 generated chord spellings and 3,000 songs through both and reports any difference.

Where the languages differ, the TypeScript side says so in its types: `transpositionTable(...).chords` is a `Map` (a plain object would reorder integer-like keys), and a `Key` is a plain `{ tonic, minor }` object checked by every function that takes one (`keyEquals` compares two).

- **CI runs a slice of that net.** `python scripts/twin_differential.py --sample-into-fixtures 500` refreshes 2,500 seeded corpus cases inside `fixtures/cases.json` (tagged `"source": "corpus"`), next to the hand-written ones.

Traps the port had to handle, worth knowing before writing any Python/TypeScript twin:

- `%` keeps the sign of the dividend in JS (`-1 % 12 === -1`), of the divisor in Python: use a `mod` helper.
- A JS object reorders integer-like keys (`"2"`, `"10"` come first) and treats `"__proto__"` specially: an ordered mapping is a `Map`.
- `re.match` anchors at the start only; in JS that is a sticky (`y`) regex whose `lastIndex` must be reset. `re.fullmatch` is `^(?:…)$`.
- Python's `\d`, `\s` and `\w` are Unicode-aware and JS's are not, or differ at the edges; `str.strip()` and `String.trim()` remove different characters.
- `^\s+|\s+$` is quadratic in JS on long runs of spaces; trim with an index loop.
- Python 3.12's `sum()` compensates float rounding and JS's left-to-right addition does not, so ties can break differently: sum in an explicit loop.
- Test runners that compare with order-blind equality (`dict ==`, `toStrictEqual`) cannot catch an ordering bug: compare JSON text.

Versions: an npm release carries the version of the Python release it was cut from (lockstep at release points, so `chordsym@X.Y.Z` on npm and PyPI are the same behaviour).

Seeded from songleaf (thorwhalen/songleaf#31). Planned: a Nashville/Roman dialect; pychord and music21 as test oracles only.
