"""Dialects: how a chord symbol is spelled, as a function into the default spelling.

A dialect is a pure function ``str -> str`` that rewrites a symbol from its own spelling
into the one :func:`chordsym.parse_chord` reads by default. Every function that reads
chord symbols takes ``dialect=``: a registered name or the function itself.

>>> resolve_dialect("chordonomicon")("Fsmin7/Cs"), resolve_dialect("harte")("Bb:min7/b7")
('F#min7/C#', 'Bbm7/Ab')
>>> list(DIALECTS)
['default', 'chordonomicon', 'harte']

Built-in names are read-only; :func:`register_dialect` adds others. ``parse_chord``
remembers results keyed on the dialect's function, so a dialect must be pure (same input,
same output).
"""

from __future__ import annotations

import re
from collections.abc import Callable, Hashable
from types import MappingProxyType

from chordsym import _grammar

#: A dialect: rewrites a chord symbol from its own spelling into the default one.
Dialect = Callable[[str], str]


def _rewriter(rules: list[tuple[str, str]]) -> Dialect:
    compiled = [(re.compile(source), replacement) for source, replacement in rules]

    def rewrite(symbol: str) -> str:
        for pattern, replacement in compiled:
            # A function replacement keeps the text literal, as the TypeScript twin does.
            symbol = pattern.sub(lambda _, r=replacement: r, symbol)
        return symbol

    return rewrite


_HARTE_RE = _grammar.compile_pattern("harte")
_ADDED = dict(_grammar.HARTE_ADDED)
_ADDED_ORDER = [degree for degree, _ in _grammar.HARTE_ADDED]


def _harte_suffix(shorthand: str, intervals: str) -> str | None:
    """The default suffix of ``shorthand`` with the degrees ``intervals`` added."""
    items = intervals.split(",")
    sevenths = [item for item in items if item in ("b7", "7", "bb7")]
    others = [item for item in items if item not in sevenths]
    if len(sevenths) > 1 or not all(item in _ADDED for item in others):
        return None
    if sevenths:
        suffix = _grammar.HARTE_SEVENTHS.get(shorthand, {}).get(sevenths[0])
    else:
        suffix = _grammar.HARTE_SHORTHANDS.get(shorthand)
    if suffix is None:
        return None
    others.sort(key=_ADDED_ORDER.index)
    return suffix + "".join(_ADDED[item] for item in others)


def harte(symbol: str) -> str:
    """A Harte label (``C:maj7``, ``A:min(9)``, ``C:(1,b3,5)``, ``C:maj/3``) in the default
    spelling; ``""`` (not a chord) for a Harte label it cannot read, the symbol unchanged
    when it is not a Harte label (``N``, ``D/F#``).

    >>> [harte(s) for s in ("C:maj/b7", "A:min(9)", "C:sus4(b7)", "C:(1,b3,5,b7)", "C:(3,5)", "N")]
    ['C/Bb', 'Amadd9', 'C7sus4', 'Cm7', '', 'N']
    """
    match = _HARTE_RE.fullmatch(symbol)
    if match is None:
        return symbol
    lead, letter, accidental, shorthand, intervals, bass, trail = match.groups()
    if shorthand is None:  # no colon: "C" is C:maj
        suffix = ""
    elif shorthand == "":  # an interval list alone: "C:(1,b3,5)"
        suffix = _grammar.HARTE_INTERVAL_SETS.get(intervals)
    elif intervals is None:
        suffix = _grammar.HARTE_SHORTHANDS.get(shorthand)
    else:
        suffix = _harte_suffix(shorthand, intervals)
    if suffix is None:
        return ""
    out = lead + letter + accidental + suffix
    if bass is not None:
        interval = _grammar.HARTE_DEGREES.get(bass)
        if interval is None:
            return ""
        root = _grammar.PITCH_CLASSES[letter] + _grammar.ACCIDENTALS[accidental]
        # Spelled with flats under a flat root, or a flat degree under a natural root.
        flats = accidental == "b" or (accidental == "" and bass.startswith("b"))
        names = _grammar.FLAT_NAMES if flats else _grammar.SHARP_NAMES
        out += "/" + names[(root + interval) % 12]
    return out + trail


_BUILTIN: dict[str, Dialect] = {
    **{name: _rewriter(rules) for name, rules in _grammar.DIALECT_REWRITES.items()},
    "harte": harte,
}
_REGISTRY: dict[str, Dialect] = dict(_BUILTIN)

#: Dialect name -> its function (read-only; add a dialect with :func:`register_dialect`).
DIALECTS = MappingProxyType(_REGISTRY)


def register_dialect(name: str, normalise: Dialect) -> Dialect:
    """Make ``normalise`` (a pure ``str -> str``) readable as ``dialect=name``; returns it.

    >>> _ = register_dialect("lower", str.capitalize)
    >>> from chordsym import parse_chord
    >>> parse_chord("am", dialect="lower")
    (9, 'minor')
    >>> unregister_dialect("lower")
    """
    if not isinstance(name, str):
        raise TypeError(f"A dialect name must be a str, not {name!r}")
    if name in _BUILTIN:
        raise ValueError(f"{name!r} is a built-in dialect and cannot be replaced")
    if not callable(normalise):
        raise TypeError(f"A dialect must be a function str -> str, not {normalise!r}")
    _REGISTRY[name] = resolve_dialect(normalise)  # checks it is hashable
    return normalise


def unregister_dialect(name: str) -> None:
    """Forget a dialect added with :func:`register_dialect` (built-ins stay)."""
    if name in _BUILTIN:
        raise ValueError(f"{name!r} is a built-in dialect and cannot be removed")
    if name not in _REGISTRY:
        raise ValueError(f"No registered dialect {name!r}; one of {list(_REGISTRY)}")
    del _REGISTRY[name]


def resolve_dialect(dialect: str | Dialect) -> Dialect:
    """The function for ``dialect``: a registered name, or a function passed as is.

    Raises ValueError for an unknown name (listing the known ones), TypeError for
    anything else, including an unhashable function (results are cached per function).
    """
    if callable(dialect):
        if not isinstance(dialect, Hashable):
            raise TypeError(
                f"A dialect function must be hashable (parse_chord caches per function): {dialect!r}"
            )
        return dialect
    if not isinstance(dialect, str):
        raise TypeError(f"dialect must be a name or a function, not {dialect!r}")
    normalise = _REGISTRY.get(dialect)
    if normalise is None:
        raise ValueError(f"Unknown dialect {dialect!r}; one of {list(_REGISTRY)}")
    return normalise
