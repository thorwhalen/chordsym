/**
 * chordsym: chord symbols without dependencies — parse, pitch classes, keys, transposition.
 *
 * The TypeScript twin of the Python package `chordsym` (same repository). Both read one
 * grammar (generated from chordsym/_grammar.py) and pass the same golden cases
 * (fixtures/cases.json). Names are camelCase; Python's keyword arguments are an options
 * object.
 *
 * @example
 * parseChord("Am7");                         // [9, "minor"]
 * transposeChord("C/E", 3, { flats: true }); // "Eb/G"
 * estimateKey(["Am", "Dm", "E7"]);           // { tonic: 9, minor: true }
 */
export { chordTones, isChordToken, parseChord, type Quality } from "./parse.js";
export { chordFunction, estimateKey, makeKey, type ChordFunction, type Key } from "./keys.js";
export {
  keyName,
  transposeChord,
  transpositionTable,
  usesFlats,
  type TranspositionTable,
} from "./transpose.js";
