import { describe, it, expect } from "vitest";
import { splitWithIds } from "@/lib/canonical-links";

describe("splitWithIds", () => {
  it("returns plain text unchanged when no IDs are present", () => {
    const result = splitWithIds("no identifiers here");
    expect(result).toEqual([{ text: "no identifiers here" }]);
  });

  it("linkifies a PMC ID", () => {
    const result = splitWithIds("See PMC12345678 for details.");
    expect(result).toContainEqual({
      text: "PMC12345678",
      url: "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12345678/",
    });
  });

  it("linkifies a PMID with colon", () => {
    const result = splitWithIds("reference PMID:9876543");
    const linked = result.find((s) => s.text === "PMID:9876543");
    expect(linked?.url).toBe("https://pubmed.ncbi.nlm.nih.gov/9876543/");
  });

  it("linkifies a MeSH ID", () => {
    const result = splitWithIds("disease MeSH:D001943");
    const linked = result.find((s) => s.text === "MeSH:D001943");
    expect(linked?.url).toContain("D001943");
  });

  it("linkifies a UMLS ID", () => {
    const result = splitWithIds("concept UMLS:C0006142");
    const linked = result.find((s) => s.text === "UMLS:C0006142");
    expect(linked?.url).toContain("C0006142");
  });

  it("preserves surrounding text as plain segments", () => {
    const result = splitWithIds("before PMC111 after");
    expect(result[0]).toEqual({ text: "before " });
    expect(result[2]).toEqual({ text: " after" });
  });

  it("handles multiple IDs in one string", () => {
    const result = splitWithIds("PMC111 and OMIM:100200");
    const ids = result.filter((s) => s.url !== undefined).map((s) => s.text);
    expect(ids).toEqual(["PMC111", "OMIM:100200"]);
  });

  it("returns empty array for empty string", () => {
    expect(splitWithIds("")).toEqual([]);
  });
});
