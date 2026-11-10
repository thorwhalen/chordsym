// Dialects as functions and the registry, which the JSON golden cases cannot express
// (tests/test_chordsym.py checks the same on the Python side).
import { describe, expect, it } from "vitest";
import {
  DIALECTS,
  estimateKey,
  parseChord,
  registerDialect,
  resolveDialect,
  unregisterDialect,
} from "./index.js";

const capitalize = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);

describe("dialects", () => {
  it("accepts a function as the dialect", () => {
    expect(parseChord("am", { dialect: capitalize })).toEqual([9, "minor"]);
  });

  it("registers a new name, but not over a built-in", () => {
    expect(registerDialect("lower", capitalize)).toBe(capitalize);
    expect(DIALECTS.has("lower")).toBe(true);
    expect(estimateKey(["am", "dm", "e7"], { dialect: "lower" })).toEqual({ tonic: 9, minor: true });
    expect(() => registerDialect("harte", capitalize)).toThrow(RangeError);
    expect(() => registerDialect("mine", "nope" as never)).toThrow(TypeError);
    unregisterDialect("lower");
    expect(DIALECTS.has("lower")).toBe(false);
    expect(() => unregisterDialect("lower")).toThrow(RangeError);
    expect(() => unregisterDialect("harte")).toThrow(RangeError);
  });

  it("keeps the built-ins read-only and rejects what is not a name or a function", () => {
    expect([...DIALECTS.keys()].slice(0, 3)).toEqual(["default", "chordonomicon", "harte"]);
    expect("set" in DIALECTS).toBe(false);
    expect(() => {
      (DIALECTS as unknown as Record<string, unknown>).get = () => undefined;
    }).toThrow(TypeError);
    expect(() => resolveDialect(null as never)).toThrow(TypeError);
    expect(() => resolveDialect("nashville")).toThrow(RangeError);
  });
});
