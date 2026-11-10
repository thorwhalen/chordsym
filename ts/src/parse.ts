/**
 * Read a chord symbol: is it one, what is its root and quality, which pitch classes it sounds.
 * TypeScript twin of chordsym/parse.py; both read the same grammar and pass fixtures/cases.json.
 * A pitch class is an integer 0-11 (C = 0, C# = 1, ... B = 11).
 */
import { ACCIDENTALS, PATTERNS, PITCH_CLASSES, WHITESPACE } from "./grammar.generated.js";

/** "open" is a suspended or power chord: no third. */
export type Quality = "major" | "minor" | "diminished" | "open";

export type PatternName = keyof typeof PATTERNS;

/** Python `re.fullmatch` */
export function whole(name: PatternName): RegExp {
  const [src, flags] = PATTERNS[name];
  return new RegExp(`^(?:${src})$`, "u" + flags);
}

/** Python `re.match`: anchored at the start only (sticky; reset lastIndex before use). */
function atStart(name: PatternName): RegExp {
  const [src, flags] = PATTERNS[name];
  return new RegExp(src, "uy" + flags);
}

/** Python `re.search` */
function anywhere(name: PatternName): RegExp {
  const [src, flags] = PATTERNS[name];
  return new RegExp(src, "u" + flags);
}

function matchesAtStart(re: RegExp, text: string): boolean {
  re.lastIndex = 0;
  return re.test(text);
}

const CHORD_RE = whole("chord");
const ROOT_RE = whole("root");
const DIMINISHED_RE = atStart("diminished");
const POWER_RE = atStart("power");
const NOTE_AT_START_RE = atStart("note");
const NOTE_RE = anywhere("note");
const MAJOR_SEVENTH_RE = anywhere("major_seventh");
const SEVENTH_RE = anywhere("seventh");
const SIXTH_RE = anywhere("sixth");
const NINTH_RE = anywhere("ninth");
const SPACES: ReadonlySet<number> = new Set(WHITESPACE);

/**
 * Python `str.strip()`: removes exactly the characters `str.isspace` accepts (all in the
 * BMP), in linear time (a `^\s+|\s+$` regex is quadratic on long runs of spaces).
 */
export function strip(text: string): string {
  let start = 0;
  let end = text.length;
  while (start < end && SPACES.has(text.charCodeAt(start))) start++;
  while (end > start && SPACES.has(text.charCodeAt(end - 1))) end--;
  return text.slice(start, end);
}

/** Python's `%`: the result has the divisor's sign, so pitch classes stay in 0-11. */
export function mod(n: number, m: number): number {
  return ((n % m) + m) % m;
}

export function pitchClass(letter: string, accidental: string): number {
  const natural = (PITCH_CLASSES as Record<string, number>)[letter];
  const offset = (ACCIDENTALS as Record<string, number>)[accidental];
  if (natural === undefined || offset === undefined) {
    throw new RangeError(`chordsym: not a note name: ${letter}${accidental}`);
  }
  return mod(natural + offset, 12);
}

/** True if `token` reads as a chord symbol (`G`, `F#m7b5`, `E7(#9)`, `C/G`). */
export function isChordToken(token: string): boolean {
  return CHORD_RE.test(token);
}

/** `[root pitch class, quality]`, or null for what is not a chord. A bass note is ignored. */
export function parseChord(symbol: string): [number, Quality] | null {
  symbol = strip(symbol);
  const match = ROOT_RE.exec(symbol);
  if (match === null || !isChordToken(symbol)) return null;
  const [, letter = "", accidental = "", rest = ""] = match;
  const root = pitchClass(letter, accidental);
  let quality: Quality;
  if (rest.startsWith("maj") || rest.startsWith("M")) quality = "major";
  else if (matchesAtStart(DIMINISHED_RE, rest)) quality = "diminished";
  else if (rest.startsWith("min") || rest.startsWith("m") || rest.startsWith("-"))
    quality = "minor"; // "C-7" is jazz for Cm7
  else if (rest.includes("sus") || matchesAtStart(POWER_RE, rest)) quality = "open";
  else quality = "major";
  return [root, quality];
}

function note(text: string): number | null {
  const re = NOTE_AT_START_RE;
  re.lastIndex = 0;
  const m = re.exec(strip(text));
  return m === null ? null : pitchClass(m[1] ?? "", m[2] ?? "");
}

/** The chord's pitch classes, bass first (the root, or the bass of a slash chord). */
export function chordTones(symbol: string): number[] | null {
  const parsed = parseChord(symbol);
  if (parsed === null) return null;
  const [root, quality] = parsed;
  const stripped = strip(symbol);
  const slash = stripped.indexOf("/");
  const head = slash < 0 ? stripped : stripped.slice(0, slash);
  const bassText = slash < 0 ? "" : stripped.slice(slash + 1);
  const rest = head.replace(NOTE_RE, "");
  const third = quality === "minor" || quality === "diminished" ? 3 : 4;
  let fifth = quality === "diminished" ? 6 : 7;
  if (rest.includes("aug") || rest.startsWith("+")) fifth = 8;
  let intervals = [0, third, fifth];
  if (quality === "open") {
    intervals = matchesAtStart(POWER_RE, rest) ? [0, 7] : [0, rest.includes("sus2") ? 2 : 5, 7];
  }
  if (rest.includes("dim7") || rest === "°7" || rest === "o7") intervals.push(9);
  else if (MAJOR_SEVENTH_RE.test(rest)) intervals.push(11);
  else if (SEVENTH_RE.test(rest)) intervals.push(10);
  if (SIXTH_RE.test(rest)) intervals.push(9);
  if (NINTH_RE.test(rest) && !intervals.includes(2)) intervals.push(2);
  let tones = [...new Set(intervals.map((i) => mod(root + i, 12)))];
  const bass = bassText ? note(bassText) : null;
  if (bass !== null) tones = [bass, ...tones.filter((t) => t !== bass)];
  return tones;
}
