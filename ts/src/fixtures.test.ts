// The golden cases in ../fixtures/cases.json, run against the TypeScript twin.
// The Python twin runs the same file (tests/test_fixtures.py).
import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import * as chordsym from "./index.js";

interface Case {
  fn: string;
  args?: unknown[];
  kwargs?: Record<string, unknown>;
  expected: unknown;
}

const { cases } = JSON.parse(
  readFileSync(new URL("../../fixtures/cases.json", import.meta.url), "utf-8"),
) as { cases: Case[] };

type AnyFn = (...args: never[]) => unknown;

/** Python name -> the TS function; keyword arguments become a trailing options object. */
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

function call(c: Case): unknown {
  const fn = FUNCTIONS[c.fn];
  if (fn === undefined) throw new Error(`no TS twin for ${c.fn}`);
  const args = [...(c.args ?? [])];
  if (c.kwargs && Object.keys(c.kwargs).length > 0) args.push(c.kwargs);
  return (fn as (...a: unknown[]) => unknown)(...args);
}

describe("fixtures/cases.json", () => {
  it("covers every function the TS twin exports", () => {
    expect(new Set(cases.map((c) => c.fn))).toEqual(new Set(Object.keys(FUNCTIONS)));
  });

  it.each(cases.map((c, i) => [`${i} ${c.fn}${JSON.stringify(c.args)}`.slice(0, 90), c] as const))(
    "%s",
    (_, c) => {
      expect(call(c)).toStrictEqual(c.expected);
    },
  );
});
