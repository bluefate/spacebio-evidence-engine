"use client";

import Link from "next/link";

import styles from "./CitationLinkedText.module.css";
import {
  publicationDetailHref,
  splitAnswerCitationMarkers,
} from "./citationMarkers";

export type CitationLinkLookup = {
  /** True when the citation id maps to a retrieved evidence passage. */
  known: boolean;
  publicationId?: string | null;
  /** False when a publication detail page is unavailable. */
  publicationAvailable?: boolean;
};

export type CitationLinkedTextProps = {
  text: string;
  /**
   * Resolve each citation marker. Missing / unknown citations should return
   * `{ known: false }` so the UI can show a broken-link state.
   */
  resolveCitation?: (citationId: string) => CitationLinkLookup;
  activeCitationId?: string | null;
  onSelectCitation?: (citationId: string) => void;
  className?: string;
};

function defaultResolve(): CitationLinkLookup {
  return { known: false };
}

export function CitationLinkedText({
  text,
  resolveCitation = defaultResolve,
  activeCitationId = null,
  onSelectCitation,
  className,
}: CitationLinkedTextProps) {
  const activeId = activeCitationId?.trim() || null;
  const segments = splitAnswerCitationMarkers(text);

  return (
    <div
      className={[styles.text, className].filter(Boolean).join(" ")}
      data-testid="citation-linked-text"
    >
      {segments.map((segment, index) => {
        if (segment.kind === "text") {
          return <span key={`t-${index}`}>{segment.value}</span>;
        }

        const lookup = resolveCitation(segment.citationId);
        const isActive = activeId === segment.citationId;
        const isBroken = !lookup.known;

        if (isBroken) {
          return (
            <span
              key={`c-${segment.citationId}-${index}`}
              className={styles.brokenMarker}
              title={`Citation ${segment.citationId} is not available in evidence`}
              data-testid={`citation-marker-broken-${segment.citationId}`}
            >
              {segment.raw}
            </span>
          );
        }

        const publicationId = lookup.publicationId?.trim() || null;
        const publicationOk = Boolean(
          publicationId && lookup.publicationAvailable !== false,
        );

        return (
          <span
            key={`c-${segment.citationId}-${index}`}
            className={styles.citationGroup}
            data-testid={`citation-group-${segment.citationId}`}
          >
            <button
              type="button"
              className={[
                styles.citationMarker,
                isActive ? styles.activeMarker : "",
              ]
                .filter(Boolean)
                .join(" ")}
              onClick={() => onSelectCitation?.(segment.citationId)}
              aria-pressed={isActive}
              data-testid={`citation-marker-${segment.citationId}`}
            >
              {segment.raw}
            </button>
            {publicationId ? (
              publicationOk ? (
                <Link
                  href={publicationDetailHref(publicationId)}
                  className={styles.publicationLink}
                  data-testid={`citation-publication-${segment.citationId}`}
                >
                  Publication
                </Link>
              ) : (
                <span
                  className={styles.brokenPublication}
                  title={`Publication ${publicationId} is not available`}
                  data-testid={`citation-publication-broken-${segment.citationId}`}
                >
                  Publication unavailable
                </span>
              )
            ) : null}
          </span>
        );
      })}
    </div>
  );
}
