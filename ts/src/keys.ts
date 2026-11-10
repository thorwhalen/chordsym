/**
 * What a chord does in a key: estimate a song's key from its chords, label chords by function.
 * TypeScript twin of chordsym/keys.py.
 */
import { KEY_WEIGHTS, MAJOR_KEY, MINOR_KEY } from "./grammar.generated.js";
import { mod, parseChord, type Quality } from "./parse.js";

/** A key: its tonic as a pitch class (C = 0, ... B = 11), major or minor. */
export interface Key {
  readonly tonic: number;
  readonly minor: boolean;
}

export function makeKey(tonic: number, minor = false): Key {
  return { tonic, minor };
}

export type ChordFunction = "tonic" | "diatonic" | "outside";

function weight(name: string): number {
  return KEY_WEIGHTS[name] ?? 0;
}

function functionIn(parsed: [number, Quality], key: Key): ChordFunction {
  const [root, quality] = parsed;
  const degree = mod(root - key.tonic, 12);
  const qualities = (key.minor ? MINOR_KEY : MAJOR_KEY)[degree];
  if (qualities === undefined || (quality !== "open" && !qualities.includes(quality))) {
    return "outside";
  }
  return degree === 0 ? "tonic" : "diatonic";
}

/** "tonic", "diatonic" or "outside" in `key`; null if `symbol` is not a chord. */
export function chordFunction(symbol: string, key: Key): ChordFunction | null {
  const parsed = parseChord(symbol);
  return parsed === null ? null : functionIn(parsed, key);
}

/**
 * The key that best explains a song's chords, in order; null if there are no chords.
 * Ties go to the major key, and to the lower tonic.
 */
export function estimateKey(symbols: Iterable<string>): Key | null {
  const chords: [number, Quality][] = [];
  for (const symbol of symbols) {
    const parsed = parseChord(symbol);
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
