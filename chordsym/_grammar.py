"""The chord-symbol grammar and tables, shared by the Python package and its TypeScript twin.

This module is the single source of truth for every regular expression and lookup table
chordsym uses. ``chordsym._codegen`` writes it to ``ts/src/grammar.generated.ts``, so the
TypeScript package reads the same patterns and tables; a test fails when the committed
TypeScript file is stale.

Every pattern here must mean the same thing in Python's ``re`` and in a JavaScript
``RegExp`` with the ``u`` flag. Hence:

- no ``\\d``, ``\\w``, ``\\s``, ``\\b`` (or their negations): Python's are Unicode-aware,
  JavaScript's are not (``\\d``) or differ at the edges (``\\s``); use ``[0-9]`` and
  :data:`WS` instead;
- ``.`` only with the DOTALL flag (``s`` in JavaScript), listed in :data:`PATTERNS`;
- whole-string matches are written by the caller (``fullmatch`` / ``^(?:...)$``), never
  with ``$`` inside a pattern.

``tests/test_grammar.py`` enforces the first rule; ``fixtures/cases.json`` checks the rest
by running the same cases on both sides.

>>> sorted(PATTERNS)[:3]
['chord', 'diminished', 'harte']
"""

import re

#: Whitespace, as a character-class body: exactly the characters Python's ``str.isspace``
#: accepts (what ``str.strip()`` removes), written out so a JavaScript ``RegExp`` (whose
#: ``\s`` lacks ``\x1c``-``\x1f`` and ``\x85`` and adds ``\ufeff``) matches the same set.
WS = (
    "\\t\\n\\x0b\\x0c\\r\\x1c\\x1d\\x1e\\x1f \\x85\\xa0\\u1680"
    "\\u2000-\\u200a\\u2028\\u2029\\u202f\\u205f\\u3000"
)

#: name -> (pattern source, flags). Flags: ``"s"`` means DOTALL.
PATTERNS: dict[str, tuple[str, str]] = {
    # Is this token a chord symbol? (used with a whole-string match)
    "chord": (
        r"[*.]{0,3}\(?"  # leading marks: *D, ...Dm6
        r"[A-G][#b]?"  # root
        # quality; o7 = °7; Δ or ∆ = maj7, mΔ7 or -Δ7 = minor-major seventh
        r"(?:maj|min|dim|aug|sus|add|[m\-]?[Δ∆]|m|M|\+|°|º|ø|o(?=7))?"
        r"[0-9]{0,2}[M+\-]?"  # extension: 7, 9, 13; Brazilian 7M, 7+, 5-
        r"(?:sus[0-9]{0,2}|(?:maj|add|dim|aug|no|m|b|#|\+|-)[0-9]{1,2}[+\-]?)*"  # b5, add9
        r"(?:/(?:[#b]?[0-9]{1,2}[+\-#b]?|sus[0-9]{0,2}))*"  # stacked: 7/9, 5-/7, 7/sus4
        r"(?:\([^()" + WS + r"]{1,10}\))*"  # parenthesised alterations: (#9), 7(4)(9)
        r"(?:/[A-G][#b]?)?"  # bass
        r"\)?\*?",
        "",
    ),
    # Lead marks, root letter, accidental, the rest (used with a whole-string match).
    "root": (r"[*.(" + WS + r"]*([A-G])([#b]?)(.*)", "s"),
    # A diminished quality, at the start of what follows the root.
    "diminished": (r"(?:dim|°|º|ø|o7|m(?:in)?7?\(?b5)", ""),
    # A power chord's 5 (not 5 of 13 or 55), at the start of what follows the root.
    "power": (r"5(?![0-9])", ""),
    # A note name: letter and optional accidental, at the start of a string.
    "note": (r"([A-G])([#b]?)", ""),
    # Seventh and extension markers, searched anywhere in what follows the root.
    # (A bare ``Δ`` or ``∆`` is a major seventh on its own: ``CΔ`` = ``Cmaj7``.)
    "major_seventh": (r"(?:maj|M)(?:7|9|11|13)|[Δ∆]", ""),
    "seventh": (r"(?<!add)(7|9|11|13)", ""),
    "sixth": (r"(?<![0-9])6", ""),
    "ninth": (r"9|add2", ""),
    # Root, suffix, and a final /bass with what trails it (used with a whole-string match).
    # The bass is only a final ``/note`` (``D/F#``); a slash inside the extension
    # (``C6/9``, ``Bm5-/7``) belongs to the chord's suffix.
    "transposable": (
        r"([*.(" + WS + r"]*)([A-G][#b]?)(.*?)(?:/([A-G][#b]?)([^/A-Za-z0-9#]*))?",
        "s",
    ),
    # A Harte label (used with a whole-string match): lead, root letter, accidental, then
    # ``:shorthand`` with an optional ``(interval list)``, then an optional ``/degree``
    # bass, then trailing whitespace. Groups: lead, letter, accidental, shorthand, list,
    # bass, trail.
    "harte": (
        r"([" + WS + r"]*)([A-G])([#b]?)"
        r"(?::([^(/" + WS + r"]*)(?:\(([^()]*)\))?)?"
        r"(?:/([#b]{0,2}[0-9]{1,2}))?([" + WS + r"]*)",
        "",
    ),
}

#: Dialect name -> the rewrites that turn its spelling into the default one, applied in
#: order as ``(pattern, replacement)``: every match of the pattern is replaced by the
#: replacement as literal text (no group references, which Python and JavaScript write
#: differently). Harte is read by structure instead (``PATTERNS["harte"]`` and the
#: ``HARTE_*`` tables), since its bass is a degree that depends on the root.
#:
#: - ``default``: the chart spellings :func:`chordsym.parse_chord` reads; no rewrite.
#: - ``chordonomicon``: the Chordonomicon corpus writes ``#`` as ``s`` (``Cs``,
#:   ``Fsmin``, ``A/Cs``, ``Emajs9``) and a power chord as ``no3d`` (``Gno3d``).
DIALECT_REWRITES: dict[str, list[tuple[str, str]]] = {
    "default": [],
    "chordonomicon": [
        (r"(?<=[A-G])s(?!us)", "#"),  # a sharp after a root or bass letter, not sus
        (r"(?<!u)s(?=[0-9])", "#"),  # a sharp before a number (majs9), not sus4
        (r"(?:(?<=[A-G])|(?<=[A-G][#b]))no3d", "5"),  # Gno3d is G5
    ],
}

#: Harte (2005) shorthands and their default spellings (``C:hdim7`` reads as ``Cm7b5``).
HARTE_SHORTHANDS = {
    "maj": "",
    "min": "m",
    "dim": "dim",
    "aug": "aug",
    "maj7": "maj7",
    "min7": "m7",
    "7": "7",
    "dim7": "dim7",
    "hdim7": "m7b5",
    "minmaj7": "mmaj7",
    "maj6": "6",
    "min6": "m6",
    "9": "9",
    "maj9": "maj9",
    "min9": "m9",
    "11": "11",
    "min11": "m11",
    "13": "13",
    "maj13": "maj13",
    "min13": "m13",
    "sus2": "sus2",
    "sus4": "sus4",
    "5": "5",
}

#: Harte interval lists without a shorthand (``C:(1,b3,5)``) that have a default spelling;
#: any other list is not read.
HARTE_INTERVAL_SETS = {
    "1,3,5": "",
    "1,b3,5": "m",
    "1,3,5,b7": "7",
    "1,b3,5,b7": "m7",
    "1,5": "5",
}

#: A seventh added in parentheses, by shorthand: ``C:min(b7)`` is ``Cm7``, ``C:sus4(b7)``
#: is ``C7sus4``, ``C:dim(b7)`` is ``Cm7b5``. A seventh added to any other shorthand is
#: not read. (Looked up only: a JavaScript object reorders integer-like keys.)
HARTE_SEVENTHS = {
    "maj": {"b7": "7", "7": "maj7"},
    "min": {"b7": "m7", "7": "mmaj7"},
    "dim": {"bb7": "dim7", "b7": "m7b5"},
    "aug": {"b7": "aug7", "7": "augmaj7"},
    "sus4": {"b7": "7sus4", "7": "sus4maj7"},
    "sus2": {"b7": "7sus2", "7": "sus2maj7"},
}

#: Other degrees added in parentheses after a shorthand (``C:maj(9)`` is ``Cadd9``), as
#: default suffix pieces appended in this order (pairs, not a mapping, because the order
#: matters and a JavaScript object would put integer-like keys first). A list with any
#: other item (an omission such as ``*3``) is not read.
HARTE_ADDED = (
    ("2", "add2"),
    ("4", "add4"),
    ("6", "add6"),
    ("9", "add9"),
    ("11", "add11"),
    ("13", "add13"),
    ("b5", "(b5)"),
    ("#5", "(#5)"),
    ("b9", "(b9)"),
    ("#9", "(#9)"),
    ("#11", "(#11)"),
    ("b13", "(b13)"),
)

#: A Harte bass degree -> semitones above the root (``C:maj/3`` has an E in the bass).
HARTE_DEGREES = {
    "1": 0,
    "b2": 1,
    "2": 2,
    "#2": 3,
    "b3": 3,
    "3": 4,
    "4": 5,
    "#4": 6,
    "b5": 6,
    "5": 7,
    "#5": 8,
    "b6": 8,
    "6": 9,
    "bb7": 9,
    "b7": 10,
    "7": 11,
    "b9": 1,
    "9": 2,
    "#9": 3,
    "11": 5,
    "#11": 6,
    "b13": 8,
    "13": 9,
}


def compile_pattern(name: str) -> re.Pattern:
    """The compiled :data:`PATTERNS` entry ``name`` (Python side only; not generated)."""
    source, flags = PATTERNS[name]
    return re.compile(source, re.DOTALL if "s" in flags else 0)


#: Natural-note pitch classes and accidental offsets.
PITCH_CLASSES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
ACCIDENTALS = {"#": 1, "b": -1, "": 0}

#: Note names by pitch class, spelled with sharps or with flats.
SHARP_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
FLAT_NAMES = ("C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B")

#: Keys whose signatures use flats, as tonic pitch classes: F Bb Eb Ab Db Gb; d g c f bb eb.
FLAT_MAJOR_TONICS = (5, 10, 3, 8, 1, 6)
FLAT_MINOR_TONICS = (2, 7, 0, 5, 10, 3)

#: Qualities each scale degree (semitones above the tonic) takes in a key.
MAJOR_KEY = {
    0: ("major",),
    2: ("minor",),
    4: ("minor",),
    5: ("major",),
    7: ("major",),
    9: ("minor",),
    11: ("diminished", "minor"),
}
MINOR_KEY = {
    0: ("minor",),
    2: ("diminished", "minor"),
    3: ("major",),
    5: ("minor",),
    7: ("minor", "major"),  # the harmonic-minor V is at home in a minor key
    8: ("major",),
    10: ("major",),
}

#: Key estimation: score of a chord that is the key's tonic, a diatonic chord, and the
#: bonus for a song starting or ending on the tonic chord.
KEY_WEIGHTS = {"tonic": 2.0, "diatonic": 1.0, "outside": 0.0, "ends": 2.0}
