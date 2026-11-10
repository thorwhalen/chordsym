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
['chord', 'diminished', 'major_seventh']
"""

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
        r"(?:maj|min|dim|aug|sus|add|m|M|\+|°|º|ø)?"  # quality
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
    "diminished": (r"(?:dim|°|º|ø|m(?:in)?7?\(?b5)", ""),
    # A power chord's 5 (not 5 of 13 or 55), at the start of what follows the root.
    "power": (r"5(?![0-9])", ""),
    # A note name: letter and optional accidental, at the start of a string.
    "note": (r"([A-G])([#b]?)", ""),
    # Seventh and extension markers, searched anywhere in what follows the root.
    "major_seventh": (r"(maj|M|Δ)(7|9|11|13)", ""),
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
}

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
