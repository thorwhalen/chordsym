/**
 * Dialects: how a chord symbol is spelled, as a function into the default spelling.
 * TypeScript twin of chordsym/dialects.py; the rewrite and Harte tables are generated from
 * chordsym/_grammar.py. A dialect must be pure (same input, same output).
 */
import {
  ACCIDENTALS,
  DIALECT_REWRITES,
  FLAT_NAMES,
  HARTE_ADDED,
  HARTE_DEGREES,
  HARTE_INTERVAL_SETS,
  HARTE_SEVENTHS,
  HARTE_SHORTHANDS,
  PATTERNS,
  PITCH_CLASSES,
  SHARP_NAMES,
} from "./grammar.generated.js";

/** A dialect: rewrites a chord symbol from its own spelling into the default one. */
export type Dialect = (symbol: string) => string;

/** How a chord symbol is spelled: a name in `DIALECTS` or a `Dialect` function. */
export interface DialectOptions {
  dialect?: string | Dialect;
}

/** Python's `dict.get`: own keys only (a plain object also answers "constructor"). */
function own<V>(table: Readonly<Record<string, V>>, key: string | undefined): V | undefined {
  return key !== undefined && Object.hasOwn(table, key) ? table[key] : undefined;
}

function rewriter(rules: readonly (readonly [string, string])[]): Dialect {
  const compiled = rules.map(([src, replacement]) => [new RegExp(src, "gu"), replacement] as const);
  return (symbol) => {
    // A function replacement keeps the text literal (no `$1`), as Python's does.
    for (const [re, replacement] of compiled) symbol = symbol.replace(re, () => replacement);
    return symbol;
  };
}

const HARTE_RE = new RegExp(`^(?:${PATTERNS.harte[0]})$`, "u" + PATTERNS.harte[1]);
// HARTE_ADDED is a list of pairs: its order matters, and an object's keys would not keep it.
const ADDED: ReadonlyMap<string, string> = new Map(HARTE_ADDED);
const ADDED_ORDER: readonly string[] = HARTE_ADDED.map(([degree]) => degree);
const SHORTHANDS: Readonly<Record<string, string>> = HARTE_SHORTHANDS;
const SEVENTHS: Readonly<Record<string, Readonly<Record<string, string>>>> = HARTE_SEVENTHS;
const INTERVAL_SETS: Readonly<Record<string, string>> = HARTE_INTERVAL_SETS;
const DEGREES: Readonly<Record<string, number>> = HARTE_DEGREES;
const SEVENTH_DEGREES: readonly string[] = ["b7", "7", "bb7"];

/** The default suffix of `shorthand` with the degrees `intervals` added. */
function harteSuffix(shorthand: string, intervals: string): string | undefined {
  const items = intervals.split(",");
  const sevenths = items.filter((item) => SEVENTH_DEGREES.includes(item));
  const others = items.filter((item) => !sevenths.includes(item));
  if (sevenths.length > 1 || !others.every((item) => ADDED.has(item))) return undefined;
  const suffix =
    sevenths.length > 0
      ? own(own(SEVENTHS, shorthand) ?? {}, sevenths[0])
      : own(SHORTHANDS, shorthand);
  if (suffix === undefined) return undefined;
  others.sort((a, b) => ADDED_ORDER.indexOf(a) - ADDED_ORDER.indexOf(b));
  return suffix + others.map((item) => ADDED.get(item)).join("");
}

/**
 * A Harte label (`C:maj7`, `A:min(9)`, `C:(1,b3,5)`, `C:maj/3`) in the default spelling; ""
 * (not a chord) for a Harte label it cannot read, the symbol unchanged when it is not a
 * Harte label (`N`, `D/F#`).
 */
export function harte(symbol: string): string {
  const match = HARTE_RE.exec(symbol);
  if (match === null) return symbol;
  const [, lead = "", letter = "", accidental = "", shorthand, intervals, bass, trail = ""] = match;
  let suffix: string | undefined;
  if (shorthand === undefined) suffix = ""; // no colon: "C" is C:maj
  else if (shorthand === "") suffix = own(INTERVAL_SETS, intervals); // "C:(1,b3,5)"
  else if (intervals === undefined) suffix = own(SHORTHANDS, shorthand);
  else suffix = harteSuffix(shorthand, intervals);
  if (suffix === undefined) return "";
  let out = lead + letter + accidental + suffix;
  if (bass !== undefined) {
    const interval = own(DEGREES, bass);
    if (interval === undefined) return "";
    const root =
      (PITCH_CLASSES as Record<string, number>)[letter]! +
      (ACCIDENTALS as Record<string, number>)[accidental]!;
    // Spelled with flats under a flat root, or a flat degree under a natural root.
    const flats = accidental === "b" || (accidental === "" && bass.startsWith("b"));
    const names = flats ? FLAT_NAMES : SHARP_NAMES;
    out += "/" + names[(((root + interval) % 12) + 12) % 12];
  }
  return out + trail;
}

const BUILTIN: ReadonlyMap<string, Dialect> = new Map<string, Dialect>([
  ...Object.entries(DIALECT_REWRITES).map(([name, rules]) => [name, rewriter(rules)] as const),
  ["harte", harte],
]);
const REGISTRY = new Map<string, Dialect>(BUILTIN);

const view: ReadonlyMap<string, Dialect> = {
  get: (name) => REGISTRY.get(name),
  has: (name) => REGISTRY.has(name),
  get size() {
    return REGISTRY.size;
  },
  keys: () => REGISTRY.keys(),
  values: () => REGISTRY.values(),
  entries: () => REGISTRY.entries(),
  forEach: (fn, thisArg) => REGISTRY.forEach((v, k) => fn.call(thisArg, v, k, DIALECTS)),
  [Symbol.iterator]: () => REGISTRY[Symbol.iterator](),
};
/** Dialect name -> its function (read-only; add a dialect with `registerDialect`). */
export const DIALECTS: ReadonlyMap<string, Dialect> = Object.freeze(view);

/** Make `normalise` (a pure string -> string) readable as `{ dialect: name }`; returns it. */
export function registerDialect(name: string, normalise: Dialect): Dialect {
  if (typeof name !== "string") throw new TypeError(`chordsym: a dialect name must be a string`);
  if (BUILTIN.has(name)) {
    throw new RangeError(`chordsym: ${JSON.stringify(name)} is a built-in dialect and cannot be replaced`);
  }
  if (typeof normalise !== "function") {
    throw new TypeError(`chordsym: a dialect must be a function string -> string`);
  }
  REGISTRY.set(name, normalise);
  return normalise;
}

/** Forget a dialect added with `registerDialect` (built-ins stay). */
export function unregisterDialect(name: string): void {
  if (BUILTIN.has(name)) {
    throw new RangeError(`chordsym: ${JSON.stringify(name)} is a built-in dialect and cannot be removed`);
  }
  if (!REGISTRY.delete(name)) {
    throw new RangeError(`chordsym: no registered dialect ${JSON.stringify(name)}`);
  }
}

/**
 * The function for `dialect` (default "default"): a registered name, or a function passed as
 * is. Throws RangeError (Python: ValueError) for an unknown name, TypeError for anything else.
 */
export function resolveDialect(dialect: string | Dialect = "default"): Dialect {
  if (typeof dialect === "function") return dialect;
  if (typeof dialect !== "string") {
    throw new TypeError(`chordsym: dialect must be a name or a function, not ${String(dialect)}`);
  }
  const normalise = REGISTRY.get(dialect);
  if (normalise === undefined) {
    throw new RangeError(
      `chordsym: unknown dialect ${JSON.stringify(dialect)}; one of ${JSON.stringify([...REGISTRY.keys()])}`,
    );
  }
  return normalise;
}
