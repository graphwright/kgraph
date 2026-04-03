/**
 * Maps canonical ID prefixes to their authoritative web URLs.
 * Each entry: { pattern, url } where url is a function from the full match to a URL string.
 */

interface IdPattern {
  pattern: RegExp;
  url: (match: string) => string;
}

export const ID_PATTERNS: IdPattern[] = [
  {
    // PMC12345678
    pattern: /\bPMC\d+\b/g,
    url: (m) => `https://www.ncbi.nlm.nih.gov/pmc/articles/${m}/`,
  },
  {
    // PMID:12345678 or PMID12345678
    pattern: /\bPMID:?\d+\b/g,
    url: (m) => `https://pubmed.ncbi.nlm.nih.gov/${m.replace(/^PMID:?/, "")}/`,
  },
  {
    // MeSH:D003480
    pattern: /\bMeSH:[A-Z]\d+\b/g,
    url: (m) => `https://meshb.nlm.nih.gov/record/ui?ui=${m.replace("MeSH:", "")}`,
  },
  {
    // UMLS:C0001234
    pattern: /\bUMLS:[A-Z]\d+\b/g,
    url: (m) => `https://uts.nlm.nih.gov/uts/umls/concept/${m.replace("UMLS:", "")}`,
  },
  {
    // OMIM:100200
    pattern: /\bOMIM:\d+\b/g,
    url: (m) => `https://www.omim.org/entry/${m.replace("OMIM:", "")}`,
  },
  {
    // CHEBI:15422
    pattern: /\bCHEBI:\d+\b/g,
    url: (m) => `https://www.ebi.ac.uk/chebi/searchId.do?chebiId=${m}`,
  },
  {
    // UniProt: P12345 or Q9UKT9 (6-char alphanumeric starting with letter)
    pattern: /\bUniProt:[A-Z][A-Z0-9]{5}\b/g,
    url: (m) => `https://www.uniprot.org/uniprot/${m.replace("UniProt:", "")}`,
  },
  {
    // DO:DOID:1234 or DOID:1234
    pattern: /\bDOID:\d+\b/g,
    url: (m) => `https://www.disease-ontology.org/term/${m}/`,
  },
];

/**
 * Split a text string into segments, tagging any canonical ID matches with their URL.
 * Returns an array of { text, url? } — url is set only for matched IDs.
 */
export function splitWithIds(text: string): Array<{ text: string; url?: string }> {
  // Build a combined pattern that matches any ID
  const combined = new RegExp(ID_PATTERNS.map((p) => p.pattern.source).join("|"), "g");

  const result: Array<{ text: string; url?: string }> = [];
  let last = 0;
  let match: RegExpExecArray | null;

  while ((match = combined.exec(text)) !== null) {
    if (match.index > last) {
      result.push({ text: text.slice(last, match.index) });
    }
    const matched = match[0];
    // Find which pattern produced this match
    const pattern = ID_PATTERNS.find((p) => {
      const r = new RegExp(`^(?:${p.pattern.source})$`);
      return r.test(matched);
    });
    result.push({ text: matched, url: pattern?.url(matched) });
    last = match.index + matched.length;
  }

  if (last < text.length) {
    result.push({ text: text.slice(last) });
  }

  return result;
}
