import corpus from "@/data/corpus.json";

import { formatLabel, formatLicense, type CorpusPublication } from "@/data/corpus";

export type PublicationSearchResult = {
  kind: "publication";
  publicationId: string;
  title: string;
  doi: string;
  year: string;
  license: string;
  organism: string;
  exposure: string;
  sourceUrl: string;
  pdfUrl: string;
  notes: string;
  approval: string;
  ingestion: string;
};

export type PassageSearchResult = {
  kind: "passage";
  chunkId: string;
  publicationId: string;
  title: string;
  section: string;
  pageStart: number | null;
  pageEnd: number | null;
  sourceUrl: string;
  excerpt: string;
};

export type SearchResponse = {
  query: string;
  total: number;
  source: "inventory" | "indexed" | "mixed";
  publications: PublicationSearchResult[];
  passages: PassageSearchResult[];
};

type StoredChunk = {
  chunk_id?: unknown;
  chunkId?: unknown;
  publication_id?: unknown;
  publicationId?: unknown;
  section?: unknown;
  page_start?: unknown;
  pageStart?: unknown;
  page_end?: unknown;
  pageEnd?: unknown;
  chunk_text?: unknown;
  chunkText?: unknown;
  excerpt?: unknown;
};

const publications = corpus as CorpusPublication[];

export function searchStoredCorpus(query: string, limit = 20): SearchResponse {
  const normalizedQuery = query.trim();
  if (!normalizedQuery) {
    return { query: "", total: 0, source: "inventory", publications: [], passages: [] };
  }

  const terms = normalizedQuery.toLowerCase().split(/\s+/).filter(Boolean);
  const publicationMatches = publications
    .map((publication) => ({
      publication,
      score: scorePublication(publication, terms),
    }))
    .filter((item) => item.score > 0)
    .sort(
      (left, right) =>
        right.score - left.score || left.publication.id.localeCompare(right.publication.id),
    )
    .slice(0, limit)
    .map(({ publication }) => toPublicationResult(publication));

  const passageMatches = publications
    .flatMap((publication) => findPassageMatches(publication, terms))
    .sort((left, right) => right.score - left.score || left.result.chunkId.localeCompare(right.result.chunkId))
    .slice(0, limit)
    .map(({ result }) => result);

  return {
    query: normalizedQuery,
    total: publicationMatches.length + passageMatches.length,
    source: passageMatches.length > 0 ? "mixed" : "inventory",
    publications: publicationMatches,
    passages: passageMatches,
  };
}

type IndexedPassagePayload = {
  chunk_id?: unknown;
  chunkId?: unknown;
  publication_id?: unknown;
  publicationId?: unknown;
  title?: unknown;
  section?: unknown;
  page_start?: unknown;
  pageStart?: unknown;
  page_end?: unknown;
  pageEnd?: unknown;
  source_url?: unknown;
  sourceUrl?: unknown;
  excerpt?: unknown;
};

export function mergeInventoryAndIndexedSearch(
  inventory: SearchResponse,
  indexed: { source?: unknown; passages?: unknown },
): SearchResponse {
  const indexedPassages = Array.isArray(indexed.passages)
    ? indexed.passages.flatMap((item) => {
        const mapped = toIndexedPassage(item as IndexedPassagePayload);
        return mapped ? [mapped] : [];
      })
    : [];
  const usedIndexed = indexed.source === "indexed" && indexedPassages.length > 0;
  const passages = usedIndexed ? indexedPassages : inventory.passages;
  return {
    query: inventory.query,
    publications: inventory.publications,
    passages,
    total: inventory.publications.length + passages.length,
    source: usedIndexed ? (inventory.publications.length > 0 ? "mixed" : "indexed") : inventory.source,
  };
}

function toIndexedPassage(stored: IndexedPassagePayload): PassageSearchResult | null {
  const chunkId = stringValue(stored.chunk_id) ?? stringValue(stored.chunkId);
  const publicationId = stringValue(stored.publication_id) ?? stringValue(stored.publicationId);
  const title = stringValue(stored.title);
  const section = stringValue(stored.section);
  const excerpt = stringValue(stored.excerpt);
  const sourceUrl = stringValue(stored.source_url) ?? stringValue(stored.sourceUrl);
  if (!chunkId || !publicationId || !title || !section || !excerpt || !sourceUrl) {
    return null;
  }
  return {
    kind: "passage",
    chunkId,
    publicationId,
    title,
    section,
    pageStart: numberValue(stored.page_start) ?? numberValue(stored.pageStart),
    pageEnd: numberValue(stored.page_end) ?? numberValue(stored.pageEnd),
    sourceUrl,
    excerpt,
  };
}

function scorePublication(publication: CorpusPublication, terms: string[]): number {
  const title = publication.title.toLowerCase();
  const haystack = [
    publication.id,
    publication.title,
    publication.doi,
    publication.year,
    publication.license,
    publication.organism,
    publication.exposure,
    publication.notes,
    publication.approval,
    publication.ingestion,
    ...(publication.sections ?? []),
  ]
    .join(" ")
    .toLowerCase();

  return terms.reduce((score, term) => {
    if (title.includes(term)) {
      return score + 4;
    }
    if (haystack.includes(term)) {
      return score + 1;
    }
    return score;
  }, 0);
}

function findPassageMatches(
  publication: CorpusPublication,
  terms: string[],
): Array<{ result: PassageSearchResult; score: number }> {
  if (!Array.isArray(publication.chunks)) {
    return [];
  }

  return publication.chunks.flatMap((chunk) => {
    const stored = chunk as StoredChunk;
    const text = stringValue(stored.chunk_text) ?? stringValue(stored.chunkText) ?? stringValue(stored.excerpt);
    const chunkId = stringValue(stored.chunk_id) ?? stringValue(stored.chunkId);
    const section = stringValue(stored.section);
    if (!text || !chunkId || !section) {
      return [];
    }

    const lowerText = text.toLowerCase();
    const score = terms.reduce((sum, term) => (lowerText.includes(term) ? sum + 1 : sum), 0);
    if (score === 0) {
      return [];
    }

    return [
      {
        score,
        result: {
          kind: "passage" as const,
          chunkId,
          publicationId:
            stringValue(stored.publication_id) ?? stringValue(stored.publicationId) ?? publication.id,
          title: publication.title,
          section,
          pageStart: numberValue(stored.page_start) ?? numberValue(stored.pageStart),
          pageEnd: numberValue(stored.page_end) ?? numberValue(stored.pageEnd),
          sourceUrl: publication.sourceUrl,
          excerpt: text,
        },
      },
    ];
  });
}

function toPublicationResult(publication: CorpusPublication): PublicationSearchResult {
  return {
    kind: "publication",
    publicationId: publication.id,
    title: publication.title,
    doi: publication.doi,
    year: publication.year,
    license: formatLicense(publication.license),
    organism: formatLabel(publication.organism),
    exposure: formatLabel(publication.exposure),
    sourceUrl: publication.sourceUrl,
    pdfUrl: publication.pdfUrl,
    notes: publication.notes,
    approval: formatLabel(publication.approval),
    ingestion: formatLabel(publication.ingestion),
  };
}

function stringValue(value: unknown): string | null {
  return typeof value === "string" && value.trim() ? value : null;
}

function numberValue(value: unknown): number | null {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}
