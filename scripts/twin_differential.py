"""Compare the Python and TypeScript twins on a large generated corpus (run by hand, before a release).

The golden cases in ``fixtures/cases.json`` are the standing guard in CI; this script is the
wide net behind them: it generates tens of thousands of chord spellings (every root ×
quality × extension × bass, plus seeded random strings), computes every public function on
them in Python, runs the same inputs through the built TypeScript package with Node, and
reports any difference.

    (cd ts && npm run build) && python scripts/twin_differential.py

Requires Node >= 20 and a built ``ts/dist``. Exits 1 on any mismatch.

``python scripts/twin_differential.py --sample-into-fixtures 500`` instead refreshes a seeded
sample of the corpus inside ``fixtures/cases.json``, so CI runs part of this net on both sides.
"""

from __future__ import annotations

import itertools
import json
import random
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import chordsym  # noqa: E402

ROOTS = [letter + acc for letter in "ABCDEFG" for acc in ("", "#", "b")]
QUALITIES = [
    "",
    "m",
    "M",
    "maj",
    "min",
    "dim",
    "aug",
    "sus",
    "add",
    "+",
    "°",
    "º",
    "ø",
    "-",
    "5",
]
EXTENSIONS = ["", "7", "9", "11", "13", "6", "7M", "7+", "5-", "b5", "#9", "sus2", "sus4", "add9",
              "6/9", "7/9", "4/7", "7(#9)", "(4/9)", "7(4)(9)", "m7b5", "maj7", "dim7", "/sus4",
              "(b5)", "69", "add2", "no3", "Δ7", "Δ", "o7", "o7/E"]  # fmt: skip
BASSES = ["", "/E", "/G", "/F#", "/Bb", "/C", "/9", "/b13"]
LEADS = ["", "*", "...", "(", " ", "\xa0", "　", "\x1c"]
TRAILS = ["", ")", "*", " ", "\xa0", ")*"]
SHIFTS = (-13, -1, 1, 5, 11)
DIALECTS = ("default", "chordonomicon", "harte")
#: Dialect spellings: Chordonomicon roots and suffixes, Harte shorthands, and their basses.
DIALECT_ROOTS = ["C", "Cs", "C#", "Db", "Fs", "Bb", "As", "E"]
DIALECT_SUFFIXES = ["", "min", "min7", "7", "maj7", "no3d", "sus4", "sus2", "add9", "majs9",
                    "dim7", "aug", "7sus4", "minadd11", "13"]  # fmt: skip
DIALECT_BASSES = ["", "/Cs", "/E", "/Bb", "/3", "/b7", "(9)", " "]
HARTE_SHORTHANDS = ["maj", "min", "dim", "aug", "maj7", "min7", "7", "dim7", "hdim7", "minmaj7",
                    "maj6", "min6", "9", "maj9", "min9", "11", "min11", "13", "maj13", "min13",
                    "sus2", "sus4", "5", "(1,5)", "foo", "(3,5)"]  # fmt: skip

_NODE = r"""
import { readFileSync } from "node:fs";
const [dist, inputPath] = process.argv.slice(1);
const c = await import(dist);
const { tokens, songs, dialectTokens, dialectSongs, dialects } = JSON.parse(readFileSync(inputPath, "utf-8"));
const out = { tokens: tokens.map((t) => [c.isChordToken(t), c.parseChord(t), c.chordTones(t),
  [-13, -1, 1, 5, 11].flatMap((k) => [false, true].map((flats) => c.transposeChord(t, k, { flats })))]),
  songs: songs.map((s) => [c.estimateKey(s), ...[3, -4].map((k) => {
    const r = c.transpositionTable(s, k); return { ...r, chords: [...r.chords] }; })]),
  dialectTokens: dialectTokens.map((t) => dialects.map((dialect) => [c.isChordToken(t, { dialect }),
    c.parseChord(t, { dialect }), c.chordTones(t, { dialect })])),
  dialectSongs: dialectSongs.map((s) => dialects.map((dialect) => c.estimateKey(s, { dialect }))) };
process.stdout.write(JSON.stringify(out));
"""


def corpus(n_random: int = 3000, seed: int = 0) -> list[str]:
    """Every combination of the spelling parts above, plus seeded random strings."""
    rng = random.Random(seed)
    out = [
        r + q + e + b
        for r, q, e, b in itertools.product(ROOTS, QUALITIES, EXTENSIONS, BASSES)
    ]
    alphabet = "ABCDEFGmMajdinsuog#b+-°ø0123456789/()*. \xa0"
    for _ in range(n_random):
        body = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 6)))
        out.append(rng.choice(LEADS) + rng.choice(ROOTS) + body + rng.choice(TRAILS))
    return list(dict.fromkeys(out))


def dialect_corpus() -> list[str]:
    """Chordonomicon and Harte spellings: every root × suffix (or shorthand) × bass."""
    out = [
        r + q + b
        for r, q, b in itertools.product(
            DIALECT_ROOTS, DIALECT_SUFFIXES, DIALECT_BASSES
        )
    ]
    out += [
        r + ":" + q + b
        for r, q, b in itertools.product(
            DIALECT_ROOTS, HARTE_SHORTHANDS, DIALECT_BASSES
        )
    ]
    return list(dict.fromkeys(out + ["N", "X", "<verse_1>"]))  # fmt: skip


def python_outputs(tokens, songs, dialect_tokens=(), dialect_songs=()):
    """What the Python twin returns, in the JSON form the Node side produces."""

    def j(x):
        return json.loads(json.dumps(x))

    def table(s, k):
        r = chordsym.transposition_table(s, k)
        return {**r, "chords": [list(kv) for kv in r["chords"].items()]}

    def key(k):
        return None if k is None else {"tonic": k.tonic, "minor": k.minor}

    return {
        "tokens": [
            [chordsym.is_chord_token(t), j(chordsym.parse_chord(t)), j(chordsym.chord_tones(t)),
             [chordsym.transpose_chord(t, k, flats=f) for k in SHIFTS for f in (False, True)]]
            for t in tokens
        ],
        "songs": [[key(chordsym.estimate_key(s)), table(s, 3), table(s, -4)] for s in songs],
        "dialectTokens": [
            [[chordsym.is_chord_token(t, dialect=d), j(chordsym.parse_chord(t, dialect=d)),
              j(chordsym.chord_tones(t, dialect=d))] for d in DIALECTS]
            for t in dialect_tokens
        ],
        "dialectSongs": [[key(chordsym.estimate_key(s, dialect=d)) for d in DIALECTS] for s in dialect_songs],
    }  # fmt: skip


def sample_into_fixtures(n: int, *, seed: int = 20261110) -> int:
    """Replace the fixtures' corpus cases with a seeded sample of ``n`` generated tokens.

    Each sampled token gets the per-token calls the differential makes (is a chord, parse,
    tones, and a sharp and a flat transposition), tagged ``"source": "corpus"``; then
    ``record()`` fills the expectations. So CI runs a slice of the wide net on both sides.
    """
    from chordsym._fixtures import dumps, load, record

    data = load()
    hand = [c for c in data["cases"] if c.get("source") != "corpus"]
    seen = {c["args"][0] for c in hand if c["args"] and isinstance(c["args"][0], str)}
    pool = [t for t in corpus() if t not in seen]
    sample = random.Random(seed).sample(pool, n)
    cases = []
    for t in sample:
        for fn in ("is_chord_token", "parse_chord", "chord_tones"):
            cases.append({"fn": fn, "args": [t], "source": "corpus"})
        cases.append(
            {
                "fn": "transpose_chord",
                "args": [t, 5],
                "kwargs": {"flats": False},
                "source": "corpus",
            }
        )
        cases.append(
            {
                "fn": "transpose_chord",
                "args": [t, -1],
                "kwargs": {"flats": True},
                "source": "corpus",
            }
        )
    data["cases"] = hand + cases
    (ROOT / "fixtures" / "cases.json").write_text(dumps(data), encoding="utf-8")
    record(ROOT)
    return len(cases)


def main() -> int:
    if "--sample-into-fixtures" in sys.argv:
        n = int(sys.argv[sys.argv.index("--sample-into-fixtures") + 1])
        print(f"{sample_into_fixtures(n)} corpus cases written to fixtures/cases.json")
        return 0
    tokens = corpus()
    rng = random.Random(7)
    songs = [
        [rng.choice(tokens) for _ in range(rng.randint(0, 12))] for _ in range(3000)
    ]
    dialect_tokens = dialect_corpus()
    dialect_songs = [
        [rng.choice(dialect_tokens) for _ in range(rng.randint(0, 12))]
        for _ in range(1000)
    ]
    inputs = {
        "tokens": tokens,
        "songs": songs,
        "dialectTokens": dialect_tokens,
        "dialectSongs": dialect_songs,
        "dialects": DIALECTS,
    }
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(inputs, f, ensure_ascii=False)
    dist = (ROOT / "ts" / "dist" / "index.js").as_uri()
    node = subprocess.run(
        ["node", "--input-type=module", "-e", _NODE, dist, f.name],
        capture_output=True, text=True, check=True,
    )  # fmt: skip
    ts = json.loads(node.stdout)
    py = python_outputs(tokens, songs, dialect_tokens, dialect_songs)
    kinds = ("tokens", "songs", "dialectTokens", "dialectSongs")
    bad = [
        (kind, inputs[kind][i])
        for kind in kinds
        for i, (a, b) in enumerate(zip(ts[kind], py[kind]))
        if json.dumps(a) != json.dumps(b)
    ]
    print(
        f"{len(tokens)} tokens, {len(songs)} songs, {len(dialect_tokens)} dialect tokens "
        f"x {len(DIALECTS)} dialects, {len(dialect_songs)} dialect songs: {len(bad)} mismatches"
    )
    for kind, item in bad[:10]:
        print(" ", kind, repr(item))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
