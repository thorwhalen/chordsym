# chordsym.keys

What a chord does in a key: estimate a song’s key from its chords, label chords by function.

```pycon
>>> key = estimate_key(["G", "D", "Em", "C", "G", "D", "G"])
>>> key
Key(tonic=7, minor=False)
>>> [chord_function(symbol, key) for symbol in ["G", "Em", "C", "Bb", "N.C."]]
['tonic', 'diatonic', 'diatonic', 'outside', None]
>>> estimate_key(["Am", "Dm", "E7", "Am"])
Key(tonic=9, minor=True)
```

### Functions

| [`chord_function`](#chordsym.keys.chord_function)(symbol, key)   | `"tonic"`, `"diatonic"` or `"outside"` in `key`; None if `symbol` is not a chord.   |
|--------------------------------------------------------------------------------|-------------------------------------------------------------------------------------|
| [`estimate_key`](#chordsym.keys.estimate_key)(symbols)         | The key that best explains a song's chords, in order; None if there are no chords.  |

### Classes

| [`Key`](#chordsym.keys.Key)(tonic[, minor])   | A key: its tonic as a pitch class (C = 0, C# = 1, .   |
|------------------------------------------------------------------------|-------------------------------------------------------|

### *class* chordsym.keys.Key(tonic, minor=False)

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

A key: its tonic as a pitch class (C = 0, C# = 1, … B = 11), major or minor.

### chordsym.keys.chord_function(symbol, key)

`"tonic"`, `"diatonic"` or `"outside"` in `key`; None if `symbol` is not a chord.

* **Return type:**
  [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None)

### chordsym.keys.estimate_key(symbols)

The key that best explains a song’s chords, in order; None if there are no chords.

Each chord scores for a key when it belongs to it, and more when it is its
tonic; a song that starts or ends on a key’s tonic chord scores extra for
that key. Ties go to the major key, and to the lower tonic.

* **Return type:**
  [`Key`](#chordsym.keys.Key) | [`None`](https://docs.python.org/3/builtins/constants.html#None)
