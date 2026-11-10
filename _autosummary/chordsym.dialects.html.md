# chordsym.dialects

Dialects: how a chord symbol is spelled, as a function into the default spelling.

A dialect is a pure function `str -> str` that rewrites a symbol from its own spelling
into the one [`chordsym.parse_chord()`](chordsym.html.md#chordsym.parse_chord) reads by default. Every function that reads
chord symbols takes `dialect=`: a registered name or the function itself.

```pycon
>>> resolve_dialect("chordonomicon")("Fsmin7/Cs"), resolve_dialect("harte")("Bb:min7/b7")
('F#min7/C#', 'Bbm7/Ab')
>>> list(DIALECTS)
['default', 'chordonomicon', 'harte']
```

Built-in names are read-only; [`register_dialect()`](#chordsym.dialects.register_dialect) adds others. `parse_chord`
remembers results keyed on the dialect’s function, so a dialect must be pure (same input,
same output).

### Module Attributes

| [`Dialect`](#chordsym.dialects.Dialect)   | rewrites a chord symbol from its own spelling into the default one.                                                               |
|------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------|
| [`DIALECTS`](#chordsym.dialects.DIALECTS)  | Dialect name -> its function (read-only; add a dialect with [`register_dialect()`](#chordsym.dialects.register_dialect)). |

### Functions

| [`harte`](#chordsym.dialects.harte)(symbol)                     | A Harte label (`C:maj7`, `A:min(9)`, `C:(1,b3,5)`, `C:maj/3`) in the default spelling; `""` (not a chord) for a Harte label it cannot read, the symbol unchanged when it is not a Harte label (`N`, `D/F#`).   |
|------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [`register_dialect`](#chordsym.dialects.register_dialect)(name, normalise) | Make `normalise` (a pure `str -> str`) readable as `dialect=name`; returns it.                                                                                                                                 |
| [`resolve_dialect`](#chordsym.dialects.resolve_dialect)(dialect)          | The function for `dialect`: a registered name, or a function passed as is.                                                                                                                                     |
| [`unregister_dialect`](#chordsym.dialects.unregister_dialect)(name)          | Forget a dialect added with [`register_dialect()`](#chordsym.dialects.register_dialect) (built-ins stay).                                                                                              |

### chordsym.dialects.DIALECTS *= mappingproxy({'default': <function \_rewriter.<locals>.rewrite>, 'chordonomicon': <function \_rewriter.<locals>.rewrite>, 'harte': <function harte>})*

Dialect name -> its function (read-only; add a dialect with [`register_dialect()`](#chordsym.dialects.register_dialect)).

### chordsym.dialects.Dialect

rewrites a chord symbol from its own spelling into the default one.

* **Type:**
  A dialect

alias of [`Callable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Callable)[[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)], [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)]

### chordsym.dialects.harte(symbol)

A Harte label (`C:maj7`, `A:min(9)`, `C:(1,b3,5)`, `C:maj/3`) in the default
spelling; `""` (not a chord) for a Harte label it cannot read, the symbol unchanged
when it is not a Harte label (`N`, `D/F#`).

```pycon
>>> [harte(s) for s in ("C:maj/b7", "A:min(9)", "C:sus4(b7)", "C:(1,b3,5,b7)", "C:(3,5)", "N")]
['C/Bb', 'Amadd9', 'C7sus4', 'Cm7', '', 'N']
```

* **Return type:**
  [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

### chordsym.dialects.register_dialect(name, normalise)

Make `normalise` (a pure `str -> str`) readable as `dialect=name`; returns it.

```pycon
>>> _ = register_dialect("lower", str.capitalize)
>>> from chordsym import parse_chord
>>> parse_chord("am", dialect="lower")
(9, 'minor')
>>> unregister_dialect("lower")
```

* **Return type:**
  [`Callable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Callable)[[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)], [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)]

### chordsym.dialects.resolve_dialect(dialect)

The function for `dialect`: a registered name, or a function passed as is.

Raises ValueError for an unknown name (listing the known ones), TypeError for
anything else, including an unhashable function (results are cached per function).

* **Return type:**
  [`Callable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Callable)[[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)], [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)]

### chordsym.dialects.unregister_dialect(name)

Forget a dialect added with [`register_dialect()`](#chordsym.dialects.register_dialect) (built-ins stay).

* **Return type:**
  [`None`](https://docs.python.org/3/builtins/constants.html#None)
