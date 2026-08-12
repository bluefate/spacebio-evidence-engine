"use client";

import { useMemo, useState } from "react";

import { CitationLinkedText } from "./CitationLinkedText";
import { EvidencePanel } from "./EvidencePanel";
import {
  type EvidencePassage,
  toEvidencePassage,
  type PassageCitationLike,
} from "./types";

export type AnswerEvidenceViewProps = {
  answerText: string;
  passages?: readonly EvidencePassage[] | readonly PassageCitationLike[];
  /** Optional allow-list of publication detail page ids. */
  knownPublicationIds?: ReadonlySet<string> | readonly string[];
  initialActiveCitationId?: string | null;
  className?: string;
};

function normalizePassages(
  passages: AnswerEvidenceViewProps["passages"],
): EvidencePassage[] {
  if (!passages?.length) {
    return [];
  }
  return passages
    .map((item) => toEvidencePassage(item as PassageCitationLike))
    .filter((item): item is EvidencePassage => item !== null);
}

function toIdSet(
  value: AnswerEvidenceViewProps["knownPublicationIds"],
): Set<string> | null {
  if (value == null) {
    return null;
  }
  return value instanceof Set ? new Set(value) : new Set(value);
}

/**
 * Wires answer citation markers to the evidence panel and publication pages.
 * Intended for the ask page (#62) to mount once answers are rendered.
 */
export function AnswerEvidenceView({
  answerText,
  passages,
  knownPublicationIds,
  initialActiveCitationId = null,
  className,
}: AnswerEvidenceViewProps) {
  const items = useMemo(() => normalizePassages(passages), [passages]);
  const publicationAllowList = useMemo(
    () => toIdSet(knownPublicationIds),
    [knownPublicationIds],
  );
  const [activeCitationId, setActiveCitationId] = useState<string | null>(
    initialActiveCitationId,
  );

  const byId = useMemo(() => {
    const map = new Map<string, EvidencePassage>();
    for (const item of items) {
      map.set(item.citationId, item);
    }
    return map;
  }, [items]);

  return (
    <div className={className} data-testid="answer-evidence-view">
      <CitationLinkedText
        text={answerText}
        activeCitationId={activeCitationId}
        onSelectCitation={setActiveCitationId}
        resolveCitation={(citationId) => {
          const passage = byId.get(citationId);
          if (!passage) {
            return { known: false };
          }
          const publicationAvailable =
            publicationAllowList == null
              ? true
              : publicationAllowList.has(passage.publicationId);
          return {
            known: true,
            publicationId: passage.publicationId,
            publicationAvailable,
          };
        }}
      />
      <EvidencePanel
        passages={items}
        activeCitationId={activeCitationId}
        onSelectCitation={setActiveCitationId}
        knownPublicationIds={publicationAllowList ?? undefined}
      />
    </div>
  );
}
