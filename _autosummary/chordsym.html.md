# chordsym

chordsym: chord symbols without dependencies — parse, pitch classes, keys, transposition.

```pycon
>>> from chordsym import parse_chord, transpose_chord, estimate_key
>>> parse_chord("Am7"), transpose_chord("Am7", 2), estimate_key(["Am", "Dm", "E7"])
((9, 'minor'), 'Bm7', Key(tonic=9, minor=True))
```

### Modules

| [`keys`](chordsym.keys.html.md#module-chordsym.keys)           | What a chord does in a key: estimate a song's key from its chords, label chords by function.   |
|--------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------|
| [`parse`](chordsym.parse.html.md#module-chordsym.parse)         | Read a chord symbol: is it one, what is its root and quality, which pitch classes it sounds.   |
| [`transpose`](chordsym.transpose.html.md#module-chordsym.transpose) | Move chord symbols by semitones, spelled for the target key.                                   |
