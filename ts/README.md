# chordsym (TypeScript)

Chord symbols without dependencies: is this token a chord, which root and quality, which pitch classes, which key does a song's chord list suggest, and how do the chords read moved by N semitones. It reads the spellings found in scraped chord charts (`C6/9`, `Bm5-/7`, Brazilian `7M`, `E7(#9)`, `D/F#`), not only textbook ones.

```ts
import { chordTones, parseChord, transposeChord, transpositionTable, estimateKey } from "chordsym";

parseChord("F#m7");                        // [6, "minor"]
chordTones("Cmaj7");                       // [0, 4, 7, 11]  (pitch classes, C = 0)
transposeChord("C/E", 3, { flats: true }); // "Eb/G"
transpositionTable(["G", "D", "Em", "C"], 3).chords; // { G: "Bb", D: "F", Em: "Gm", C: "Eb" }
estimateKey(["Am", "Dm", "E7"]);           // { tonic: 9, minor: true }
```

This is the twin of the Python package [`chordsym`](https://pypi.org/project/chordsym/), in the same repository: both read one grammar and pass the same golden cases (`fixtures/cases.json`), so they give the same answer for the same input. See the [repository README](https://github.com/thorwhalen/chordsym#readme).
