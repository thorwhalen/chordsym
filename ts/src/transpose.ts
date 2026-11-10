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
import { resolveDialect, type DialectOptions } from "./dialects.js";
import { checkKey, estimateKey, makeKey, type Key } from "./keys.js";
import { mod, parseChord, pitchClass, whole } from "./parse.js";

/** Groups: lead, root, rest, bass, tail. */
const TRANSPOSABLE_RE = whole("transposable");

/** Whether chords in `key` are spelled with flats (Bb, Eb) rather than sharps. */
export function usesFlats(key: Key | null | undefined): boolean {
  if (key == null) return false;
  const tonics: readonly number[] = key.minor ? FLAT_MINOR_TONICS : FLAT_MAJOR_TONICS;
  return tonics.includes(checkKey(key).tonic);
}

/** Throws like Python: TypeError unless `semitones` is an integer. */
function checkSemitones(semitones: number): void {
  if (typeof semitones !== "number" || !Number.isInteger(semitones)) {
    throw new TypeError(`chordsym: semitones must be an integer, not ${semitones}`);
  }
}

/** "G", "Bb", "F#m": the key spelled as its tonic chord. */
export function keyName(key: Key, options: { flats?: boolean | null } = {}): string {
  checkKey(key);
  const flats = options.flats ?? usesFlats(key);
  return (flats ? FLAT_NAMES : SHARP_NAMES)[key.tonic] + (key.minor ? "m" : "");
}

function noteClass(name: string): number {
  return pitchClass(name[0] ?? "", name.slice(1));
}

/**
 * `symbol` moved by `semitones`: root and bass move, the rest is kept as written.
 * `flats` spells moved notes with flats. What is not a chord comes back unchanged. There is
 * no `dialect`: the output keeps the input's spelling, so only the default spelling is read.
 */
export function transposeChord(
  symbol: string,
  semitones: number,
  options: { flats?: boolean } = {},
): string {
  checkSemitones(semitones);
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
  /**
   * original -> transposed, over the distinct symbols in order of first appearance (a Map:
   * a plain object would move integer-like keys first and mishandle "__proto__").
   */
  chords: Map<string, string>;
}

/**
 * The chords of a song moved by `semitones`, spelled for the new key. `options.dialect` is
 * how `symbols` are spelled for the key estimate; each chord is moved by `transposeChord`,
 * which reads the default spelling only.
 */
export function transpositionTable(
  symbols: Iterable<string>,
  semitones: number,
  options: { key?: Key | null } & DialectOptions = {},
): TranspositionTable {
  checkSemitones(semitones);
  const dialect = resolveDialect(options.dialect);
  const list = [...symbols];
  const key = options.key ? checkKey(options.key) : estimateKey(list, { dialect });
  const target = key ? makeKey(mod(key.tonic + semitones, 12), key.minor) : null;
  const flats = usesFlats(target);
  const chords = new Map<string, string>();
  for (const symbol of list) {
    if (!chords.has(symbol)) chords.set(symbol, transposeChord(symbol, semitones, { flats }));
  }
  return { semitones, key: target ? keyName(target) : "", chords };
}
