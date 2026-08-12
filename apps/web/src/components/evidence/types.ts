/** UI model for a cited passage shown in the evidence panel (issue #63). */

export type EvidencePassage = {
  citationId: string;
  chunkId: string;
  publicationId: string;
  title?: string | null;
  section?: string | null;
  page?: number | null;
  sourceUrl?: string | null;
  /** Full or truncated passage text; prefer over excerpt when both exist. */
  passageText?: string | null;
  excerpt?: string | null;
};

/** Snake_case / API-shaped citation row from `PassageCitation` (#57). */
export type PassageCitationLike = {
  citation_id?: string;
  citationId?: string;
  chunk_id?: string;
  chunkId?: string;
  publication_id?: string;
  publicationId?: string;
  title?: string | null;
  section?: string | null;
  page?: number | null;
  source_url?: string | null;
  sourceUrl?: string | null;
  excerpt?: string | null;
  passage_text?: string | null;
  passageText?: string | null;
  chunk_text?: string | null;
  chunkText?: string | null;
};

function asNonEmptyString(value: unknown): string | null {
  if (typeof value !== "string") {
    return null;
  }
  const trimmed = value.trim();
  return trimmed.length > 0 ? trimmed : null;
}

function asOptionalPage(value: unknown): number | null {
  if (typeof value !== "number" || !Number.isFinite(value) || value < 1) {
    return null;
  }
  return Math.trunc(value);
}

/** Normalize API or UI citation objects into the panel's display model. */
export function toEvidencePassage(input: PassageCitationLike): EvidencePassage | null {
  const citationId =
    asNonEmptyString(input.citationId) ?? asNonEmptyString(input.citation_id);
  const chunkId = asNonEmptyString(input.chunkId) ?? asNonEmptyString(input.chunk_id);
  const publicationId =
    asNonEmptyString(input.publicationId) ?? asNonEmptyString(input.publication_id);

  if (!citationId || !chunkId || !publicationId) {
    return null;
  }

  const passageText =
    asNonEmptyString(input.passageText) ??
    asNonEmptyString(input.passage_text) ??
    asNonEmptyString(input.chunkText) ??
    asNonEmptyString(input.chunk_text) ??
    asNonEmptyString(input.excerpt);

  return {
    citationId,
    chunkId,
    publicationId,
    title: asNonEmptyString(input.title),
    section: asNonEmptyString(input.section),
    page: asOptionalPage(input.page),
    sourceUrl: asNonEmptyString(input.sourceUrl) ?? asNonEmptyString(input.source_url),
    passageText,
    excerpt: asNonEmptyString(input.excerpt),
  };
}

export function resolvePassageBody(passage: EvidencePassage): string | null {
  return (
    asNonEmptyString(passage.passageText) ?? asNonEmptyString(passage.excerpt) ?? null
  );
}
