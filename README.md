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

It reads the spellings found in scraped chord charts (`C6/9`, `Bm5-/7`, Brazilian `7M`, `E7(#9)`, `D/F#`), not only textbook ones. Pitch classes are ints 0-11 (C = 0).

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
- **One set of golden cases.** `fixtures/cases.json` holds about 1,500 calls with their expected results. pytest and vitest both run every one. To add a case, append it and run `python -m chordsym._fixtures`, which records the Python results; review the diff, since a changed expectation is a behaviour change on both sides.

Both packages are versioned independently; the fixtures file is the contract between them.

Seeded from songleaf (thorwhalen/songleaf#31). Planned: dialects (Harte, Chordonomicon, Nashville/Roman) as strategies; pychord and music21 as test oracles only.
