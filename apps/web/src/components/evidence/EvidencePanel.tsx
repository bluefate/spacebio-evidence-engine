"use client";

import Link from "next/link";
import { useEffect, useRef } from "react";

import { evidenceCitationDomId, publicationDetailHref } from "./citationMarkers";
import styles from "./EvidencePanel.module.css";
import {
  type EvidencePassage,
  resolvePassageBody,
  toEvidencePassage,
  type PassageCitationLike,
} from "./types";

export type EvidencePanelProps = {
  passages?: readonly EvidencePassage[] | readonly PassageCitationLike[];
  activeCitationId?: string | null;
  onSelectCitation?: (citationId: string) => void;
  /** When provided, unknown publication ids render as unavailable instead of links. */
  knownPublicationIds?: ReadonlySet<string> | readonly string[];
  heading?: string;
  className?: string;
};

function normalizePassages(
  passages: EvidencePanelProps["passages"],
): EvidencePassage[] {
  if (!passages?.length) {
    return [];
  }
  return passages
    .map((item) => toEvidencePassage(item as PassageCitationLike))
    .filter((item): item is EvidencePassage => item !== null);
}

function toIdSet(
  value: EvidencePanelProps["knownPublicationIds"],
): Set<string> | null {
  if (value == null) {
    return null;
  }
  return value instanceof Set ? new Set(value) : new Set(value);
}

function displayOrUnknown(value: string | null | undefined): string {
  const trimmed = value?.trim();
  return trimmed ? trimmed : "Unknown";
}

function formatPage(page: number | null | undefined): string {
  return typeof page === "number" && page >= 1 ? String(page) : "Unknown";
}

export function EvidencePanel({
  passages,
  activeCitationId = null,
  onSelectCitation,
  knownPublicationIds,
  heading = "Cited evidence",
  className,
}: EvidencePanelProps) {
  const items = normalizePassages(passages);
  const activeId = activeCitationId?.trim() || null;
  const activeFound = activeId ? items.some((item) => item.citationId === activeId) : true;
  const selectable = typeof onSelectCitation === "function";
  const publicationAllowList = toIdSet(knownPublicationIds);
  const activeItemRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (!activeId || !activeFound) {
      return;
    }
    const node = activeItemRef.current;
    if (node && typeof node.scrollIntoView === "function") {
      node.scrollIntoView({
        behavior: "smooth",
        block: "nearest",
      });
    }
  }, [activeId, activeFound]);

  return (
    <section
      className={[styles.panel, className].filter(Boolean).join(" ")}
      aria-label={heading}
      data-testid="evidence-panel"
    >
      <header className={styles.header}>
        <h2 className={styles.heading}>{heading}</h2>
        <p className={styles.subheading}>
          Passage text and provenance for citations in the active answer.
        </p>
      </header>

      {items.length === 0 ? (
        <p className={styles.emptyState} role="status" data-testid="evidence-empty">
          No cited passages are available for this answer.
        </p>
      ) : null}

      {activeId && !activeFound ? (
        <p className={styles.missingState} role="status" data-testid="evidence-missing-active">
          Selected citation <span className={styles.mono}>{activeId}</span> is not available
          in the retrieved evidence.
        </p>
      ) : null}

      {items.length > 0 ? (
        <ul className={styles.list} data-testid="evidence-list">
          {items.map((passage) => {
            const isActive = activeId !== null && passage.citationId === activeId;
            const body = resolvePassageBody(passage);
            const publicationAvailable =
              publicationAllowList == null
                ? true
                : publicationAllowList.has(passage.publicationId);

            return (
              <li key={passage.citationId}>
                <article
                  id={evidenceCitationDomId(passage.citationId)}
                  ref={isActive ? activeItemRef : null}
                  className={[styles.item, isActive ? styles.active : ""].filter(Boolean).join(" ")}
                  data-testid={`evidence-item-${passage.citationId}`}
                  data-active={isActive ? "true" : "false"}
                  aria-current={isActive ? "true" : undefined}
                >
                  <div className={styles.itemHeader}>
                    <span className={styles.citationBadge}>{passage.citationId}</span>
                    {selectable ? (
                      <button
                        type="button"
                        className={styles.selectButton}
                        onClick={() => onSelectCitation(passage.citationId)}
                        aria-pressed={isActive}
                        aria-label={
                          isActive
                            ? `Citation ${passage.citationId} is active`
                            : `Show cited passage ${passage.citationId}`
                        }
                      >
                        {isActive ? "Active citation" : "Show citation"}
                      </button>
                    ) : null}
                  </div>

                  <p
                    className={body ? styles.passageText : styles.missingPassage}
                    data-testid={`evidence-text-${passage.citationId}`}
                  >
                    {body ?? "Passage text unavailable for this citation."}
                  </p>

                  <dl className={styles.meta}>
                    <div className={styles.metaRow}>
                      <dt>Publication</dt>
                      <dd>
                        {publicationAvailable ? (
                          <Link
                            href={publicationDetailHref(passage.publicationId)}
                            className={styles.publicationLink}
                            data-testid={`evidence-publication-${passage.citationId}`}
                          >
                            {passage.publicationId}
                          </Link>
                        ) : (
                          <span
                            className={styles.brokenPublication}
                            data-testid={`evidence-publication-broken-${passage.citationId}`}
                            title={`Publication ${passage.publicationId} is not available`}
                            aria-label={`Publication ${passage.publicationId} is not available`}
                          >
                            {passage.publicationId} (unavailable)
                          </span>
                        )}
                        <span className={styles.titleSep}> — </span>
                        <span>{displayOrUnknown(passage.title)}</span>
                      </dd>
                    </div>
                    <div className={styles.metaRow}>
                      <dt>Section</dt>
                      <dd>{displayOrUnknown(passage.section)}</dd>
                    </div>
                    <div className={styles.metaRow}>
                      <dt>Page</dt>
                      <dd>{formatPage(passage.page)}</dd>
                    </div>
                    <div className={styles.metaRow}>
                      <dt>Chunk</dt>
                      <dd className={styles.mono}>{passage.chunkId}</dd>
                    </div>
                    {passage.sourceUrl ? (
                      <div className={styles.metaRow}>
                        <dt>Source</dt>
                        <dd>
                          <a
                            href={passage.sourceUrl}
                            className={styles.externalLink}
                            target="_blank"
                            rel="noreferrer"
                          >
                            Open source
                          </a>
                        </dd>
                      </div>
                    ) : null}
                  </dl>
                </article>
              </li>
            );
          })}
        </ul>
      ) : null}
    </section>
  );
}
