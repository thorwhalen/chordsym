/**
 * Move chord symbols by semitones, spelled for the target key.
 * TypeScript twin of chordsym/transpose.py.
 */
import {
  FLAT_MAJOR_TONICS,
  FLAT_MINOR_TONICS,
  FLAT_NAMES,
  SHARP_NAMES,
} from "./grammar.generated.js";
import { estimateKey, makeKey, type Key } from "./keys.js";
import { mod, parseChord, pitchClass, whole } from "./parse.js";

/** Groups: lead, root, rest, bass, tail. */
const TRANSPOSABLE_RE = whole("transposable");

/** Whether chords in `key` are spelled with flats (Bb, Eb) rather than sharps. */
export function usesFlats(key: Key | null | undefined): boolean {
  if (key == null) return false;
  return (key.minor ? FLAT_MINOR_TONICS : FLAT_MAJOR_TONICS).includes(key.tonic);
}

/** "G", "Bb", "F#m": the key spelled as its tonic chord. */
export function keyName(key: Key, options: { flats?: boolean | null } = {}): string {
  const flats = options.flats ?? usesFlats(key);
  return (flats ? FLAT_NAMES : SHARP_NAMES)[key.tonic] + (key.minor ? "m" : "");
}

function noteClass(name: string): number {
  return pitchClass(name[0] ?? "", name.slice(1));
}

/**
 * `symbol` moved by `semitones`: root and bass move, the rest is kept as written.
 * `flats` spells moved notes with flats. What is not a chord comes back unchanged.
 */
export function transposeChord(
  symbol: string,
  semitones: number,
  options: { flats?: boolean } = {},
): string {
  if (mod(semitones, 12) === 0 || parseChord(symbol) === null) return symbol;
  const match = TRANSPOSABLE_RE.exec(symbol);
  if (match === null) return symbol;
  const names = options.flats ? FLAT_NAMES : SHARP_NAMES;
  const moved = (name: string) => names[mod(noteClass(name) + semitones, 12)];
  const [, lead = "", root = "", rest = "", bass, tail] = match;
  let out = lead + moved(root) + rest;
  if (bass) out += "/" + moved(bass) + (tail ?? "");
  return out;
}

export interface TranspositionTable {
  semitones: number;
  /** The new key's name, "" when there are no chords. */
  key: string;
  /** original -> transposed, over the distinct chords in order of first appearance. */
  chords: Record<string, string>;
}

/** The chords of a song moved by `semitones`, spelled for the new key. */
export function transpositionTable(
  symbols: Iterable<string>,
  semitones: number,
  options: { key?: Key | null } = {},
): TranspositionTable {
  const list = [...symbols];
  const key = options.key ?? estimateKey(list);
  const target = key ? makeKey(mod(key.tonic + semitones, 12), key.minor) : null;
  const flats = usesFlats(target);
  const chords: Record<string, string> = {};
  for (const symbol of new Set(list)) chords[symbol] = transposeChord(symbol, semitones, { flats });
  return { semitones, key: target ? keyName(target) : "", chords };
}
