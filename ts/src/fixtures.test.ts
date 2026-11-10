// The golden cases in ../fixtures/cases.json, run against the TypeScript twin.
// The Python twin runs the same file (tests/test_fixtures.py); chordsym/_fixtures.py
// documents the JSON conventions this runner mirrors.
import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { PATTERNS, WHITESPACE, WS } from "./grammar.generated.js";
import * as chordsym from "./index.js";

interface Case {
  fn: string;
  args?: unknown[];
  kwargs?: Record<string, unknown>;
  expected: unknown;
}

const { functions, cases } = JSON.parse(
  readFileSync(new URL("../../fixtures/cases.json", import.meta.url), "utf-8"),
) as { functions: string[]; cases: Case[] };

type AnyFn = (...args: never[]) => unknown;

/** Python name -> the TS twin; keyword-only arguments become a trailing options object. */
const FUNCTIONS: Record<string, AnyFn> = {
  is_chord_token: chordsym.isChordToken,
  parse_chord: chordsym.parseChord,
  chord_tones: chordsym.chordTones,
  transpose_chord: chordsym.transposeChord,
  transposition_table: chordsym.transpositionTable,
  estimate_key: chordsym.estimateKey,
  chord_function: chordsym.chordFunction,
  uses_flats: chordsym.usesFlats,
  key_name: chordsym.keyName,
};

/** Results whose JSON form differs from the TS value (a Map is a list of pairs). */
const ENCODERS: Record<string, (result: never) => unknown> = {
  transposition_table: (r: chordsym.TranspositionTable) => ({ ...r, chords: [...r.chords] }),
};

/** Python exception name -> the JS error the twin throws. */
const RAISES: Record<string, string> = { ValueError: "RangeError", TypeError: "TypeError" };

function call(c: Case): unknown {
  const fn = FUNCTIONS[c.fn];
  if (fn === undefined) throw new Error(`no TS twin for ${c.fn}`);
  const args = [...(c.args ?? [])];
  if (c.kwargs && Object.keys(c.kwargs).length > 0) args.push(c.kwargs);
  try {
    const result = (fn as (...a: unknown[]) => unknown)(...args);
    const encode = ENCODERS[c.fn] as ((r: unknown) => unknown) | undefined;
    return encode ? encode(result) : result;
  } catch (error) {
    const name = Object.keys(RAISES).find((py) => RAISES[py] === (error as Error).name);
    if (name === undefined) throw error;
    return { $raises: name };
  }
}

describe("fixtures/cases.json", () => {
  it("the TS twin covers exactly the Python public functions", () => {
    expect(Object.keys(FUNCTIONS).sort()).toEqual([...functions].sort());
    expect(new Set(cases.map((c) => c.fn))).toEqual(new Set(functions));
  });

  it.each(cases.map((c, i) => [`${i} ${c.fn}${JSON.stringify(c.args)}`.slice(0, 90), c] as const))(
    "%s",
    (_, c) => {
      // Compared as JSON text: order matters, as it does on the Python side.
      expect(JSON.stringify(call(c))).toBe(JSON.stringify(c.expected));
    },
  );
});

describe("grammar.generated.ts", () => {
  it("WS matches exactly the code points Python's str.isspace accepts", () => {
    const ws = new RegExp(`^[${WS}]$`, "u");
    const matched: number[] = [];
    for (let c = 0; c <= 0x10ffff; c++) {
      if (c >= 0xd800 && c <= 0xdfff) continue; // lone surrogates: not whitespace either side
      if (ws.test(String.fromCodePoint(c))) matched.push(c);
    }
    expect(matched).toEqual([...WHITESPACE]);
  });

  it("every pattern compiles in u mode", () => {
    for (const [src, flags] of Object.values(PATTERNS)) expect(() => new RegExp(src, "u" + flags)).not.toThrow();
  });

  it("strip is linear on long runs of whitespace", () => {
    const start = performance.now();
    expect(chordsym.parseChord("C" + " ".repeat(200_000) + "x")).toBeNull();
    expect(performance.now() - start).toBeLessThan(1000);
  });
});
