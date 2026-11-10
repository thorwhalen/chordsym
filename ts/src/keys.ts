/**
 * What a chord does in a key: estimate a song's key from its chords, label chords by function.
 * TypeScript twin of chordsym/keys.py.
 */
import { KEY_WEIGHTS, MAJOR_KEY, MINOR_KEY } from "./grammar.generated.js";
import { resolveDialect, type DialectOptions } from "./dialects.js";
import { mod, parseChord, type Quality } from "./parse.js";

/** A key: its tonic as a pitch class (C = 0, ... B = 11), major or minor. */
export interface Key {
  readonly tonic: number;
  readonly minor: boolean;
}

/** Throws like Python's `Key(...)`: TypeError for a non-integer tonic, RangeError outside 0-11. */
export function checkKey(key: Key): Key {
  if (typeof key.tonic !== "number" || !Number.isInteger(key.tonic)) {
    throw new TypeError(`chordsym: Key tonic must be an integer pitch class, not ${key.tonic}`);
  }
  if (key.tonic < 0 || key.tonic > 11) {
    throw new RangeError(`chordsym: Key tonic must be 0-11 (C = 0), not ${key.tonic}`);
  }
  return key;
}

export function makeKey(tonic: number, minor = false): Key {
  return checkKey({ tonic, minor });
}

/** Python's `Key.__eq__`: same tonic and mode. */
export function keyEquals(a: Key | null | undefined, b: Key | null | undefined): boolean {
  if (a == null || b == null) return a == b;
  return a.tonic === b.tonic && a.minor === b.minor;
}

const MAJOR: Readonly<Record<number, readonly string[]>> = MAJOR_KEY;
const MINOR: Readonly<Record<number, readonly string[]>> = MINOR_KEY;
const WEIGHTS: Readonly<Record<string, number>> = KEY_WEIGHTS;

export type ChordFunction = "tonic" | "diatonic" | "outside";

function weight(name: string): number {
  return WEIGHTS[name] ?? 0;
}

function functionIn(parsed: [number, Quality], key: Key): ChordFunction {
  const [root, quality] = parsed;
  const degree = mod(root - key.tonic, 12);
  const qualities = (key.minor ? MINOR : MAJOR)[degree];
  if (qualities === undefined || (quality !== "open" && !qualities.includes(quality))) {
    return "outside";
  }
  return degree === 0 ? "tonic" : "diatonic";
}

/** "tonic", "diatonic" or "outside" in `key`; null if `symbol` is not a chord. */
export function chordFunction(
  symbol: string,
  key: Key,
  options: DialectOptions = {},
): ChordFunction | null {
  checkKey(key);
  const parsed = parseChord(symbol, options);
  return parsed === null ? null : functionIn(parsed, key);
}

/**
 * The key that best explains a song's chords, in order; null if there are no chords.
 * Ties go to the major key, and to the lower tonic. `options.dialect` names how `symbols` are
 * spelled, as in `parseChord`.
 */
export function estimateKey(symbols: Iterable<string>, options: DialectOptions = {}): Key | null {
  const dialect = resolveDialect(options.dialect); // an unknown dialect throws, even with no symbols
  const chords: [number, Quality][] = [];
  for (const symbol of symbols) {
    const parsed = parseChord(symbol, { dialect });
    if (parsed !== null) chords.push(parsed);
  }
  if (chords.length === 0) return null;
  const ends = [chords[0]!, chords[chords.length - 1]!];
  let best: Key | null = null;
  let bestScore = -Infinity;
  for (let tonic = 0; tonic < 12; tonic++) {
    for (const minor of [false, true]) {
      const key = makeKey(tonic, minor);
      let score = 0;
      for (const parsed of chords) score += weight(functionIn(parsed, key));
      for (const parsed of ends) if (functionIn(parsed, key) === "tonic") score += weight("ends");
      if (score > bestScore) {
        best = key;
        bestScore = score;
      }
    }
  }
  return best;
}
