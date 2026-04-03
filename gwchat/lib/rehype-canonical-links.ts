/**
 * Rehype plugin that walks text nodes and turns canonical IDs (PMC, MeSH, etc.)
 * into anchor elements.
 */

import { visit } from "unist-util-visit";
import { Text, Element, Root } from "hast";
import { Plugin } from "unified";
import { ID_PATTERNS } from "./canonical-links";

const COMBINED = new RegExp(ID_PATTERNS.map((p) => `(?:${p.pattern.source})`).join("|"), "g");

const rehypeCanonicalLinks: Plugin<[], Root> = () => {
  return (tree) => {
    visit(tree, "text", (node: Text, index, parent) => {
      if (!parent || index === undefined) return;
      // Don't linkify text inside existing <a> tags
      if ((parent as Element).tagName === "a") return;

      const text = node.value;
      COMBINED.lastIndex = 0;

      const segments: (Text | Element)[] = [];
      let last = 0;
      let match: RegExpExecArray | null;

      while ((match = COMBINED.exec(text)) !== null) {
        if (match.index > last) {
          segments.push({ type: "text", value: text.slice(last, match.index) });
        }
        const matched = match[0];
        const pattern = ID_PATTERNS.find((p) => {
          const r = new RegExp(`^(?:${p.pattern.source})$`);
          return r.test(matched);
        });
        const href = pattern?.url(matched) ?? "#";
        segments.push({
          type: "element",
          tagName: "a",
          properties: { href, target: "_blank", rel: "noopener noreferrer" },
          children: [{ type: "text", value: matched }],
        });
        last = match.index + matched.length;
      }

      if (segments.length === 0) return; // no matches, leave unchanged

      if (last < text.length) {
        segments.push({ type: "text", value: text.slice(last) });
      }

      // Replace the single text node with our mixed segments
      parent.children.splice(index, 1, ...segments);
    });
  };
};

export default rehypeCanonicalLinks;
