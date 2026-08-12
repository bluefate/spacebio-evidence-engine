/** Helpers for `[C1]`-style citation markers in answer text (issue #66). */

export const CITATION_MARKER_RE = /\[([A-Za-z][A-Za-z0-9_-]*)\]/g;

export type AnswerTextSegment =
  | { kind: "text"; value: string }
  | { kind: "citation"; citationId: string; raw: string };

/** Split answer prose into plain text and citation marker segments. */
export function splitAnswerCitationMarkers(text: string): AnswerTextSegment[] {
  const segments: AnswerTextSegment[] = [];
  const pattern = new RegExp(CITATION_MARKER_RE.source, "g");
  let lastIndex = 0;
  let match: RegExpExecArray | null = pattern.exec(text);

  while (match) {
    const start = match.index;
    if (start > lastIndex) {
      segments.push({ kind: "text", value: text.slice(lastIndex, start) });
    }
    segments.push({
      kind: "citation",
      citationId: match[1],
      raw: match[0],
    });
    lastIndex = start + match[0].length;
    match = pattern.exec(text);
  }

  if (lastIndex < text.length) {
    segments.push({ kind: "text", value: text.slice(lastIndex) });
  }

  return segments;
}

export function uniqueCitationIdsFromText(text: string): string[] {
  const seen = new Set<string>();
  const ids: string[] = [];
  for (const segment of splitAnswerCitationMarkers(text)) {
    if (segment.kind !== "citation" || seen.has(segment.citationId)) {
      continue;
    }
    seen.add(segment.citationId);
    ids.push(segment.citationId);
  }
  return ids;
}

export function publicationDetailHref(publicationId: string): string {
  return `/publications/${encodeURIComponent(publicationId)}`;
}

export function evidenceCitationDomId(citationId: string): string {
  return `evidence-citation-${citationId}`;
}
