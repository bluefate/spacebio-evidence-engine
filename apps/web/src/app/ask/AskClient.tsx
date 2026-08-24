"use client";

import { FormEvent, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";

import { CitationLinkedText, EvidencePanel } from "@/components/evidence";
import type { CitationLinkLookup } from "@/components/evidence";
import { askQuestion, type GroundedAnswerResponse } from "@/data/ask";

import styles from "./ask.module.css";

const emptyResponse: GroundedAnswerResponse = {
  schema_version: "1.0.0",
  question: "",
  answer_text: "",
  claims: [],
  citations: [],
  sufficiency: {
    status: "insufficient",
    reason: null,
    retrieved_chunk_count: 0,
    supporting_publication_count: 0,
  },
};

export function AskClient() {
  const searchParams = useSearchParams();
  const [question, setQuestion] = useState(searchParams.get("q")?.trim() ?? "");
  const [topK, setTopK] = useState(8);
  const [response, setResponse] =
    useState<GroundedAnswerResponse>(emptyResponse);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeCitationId, setActiveCitationId] = useState<string | null>(null);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = question.trim();
    setSearched(true);
    setError(null);
    setActiveCitationId(null);

    if (!trimmed) {
      setResponse(emptyResponse);
      return;
    }

    setLoading(true);
    const result = await askQuestion({ question: trimmed, top_k: topK });
    if (result.error) {
      setError(result.error.message);
      setResponse(emptyResponse);
    } else if (result.response) {
      setResponse(result.response);
      if (result.response.citations.length > 0) {
        setActiveCitationId(result.response.citations[0].citation_id);
      }
    }
    setLoading(false);
  }

  const isInsufficient = response.sufficiency.status === "insufficient";
  const hasAnswer = response.answer_text.trim().length > 0;
  const hasCitations = response.citations.length > 0;
  const hasClaims = response.claims.length > 0;

  const citationLookup = useMemo(() => {
    const map = new Map<string, CitationLinkLookup>();
    for (const citation of response.citations) {
      map.set(citation.citation_id, {
        known: true,
        publicationId: citation.publication_id,
      });
    }
    return map;
  }, [response.citations]);

  function resolveCitation(citationId: string): CitationLinkLookup {
    return citationLookup.get(citationId) ?? { known: false };
  }

  return (
    <section className={styles.askPanel} aria-labelledby="ask-heading">
      <div className={styles.panelHeader}>
        <h2 id="ask-heading">Grounded question</h2>
        <p className={styles.helpText}>
          The first block is the answer. Everything below it is supporting
          material: claims, warnings, and quoted PDF passages for each{" "}
          <code className={styles.inlineCode}>[C1]</code> marker. Paper titles
          under a quote are provenance, not the evidence.
        </p>
      </div>

      <form className={styles.askForm} onSubmit={onSubmit}>
        <label className={styles.label} htmlFor="ask-question">
          Research question
        </label>
        <textarea
          id="ask-question"
          name="question"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="How does microgravity affect skeletal muscle proteome changes in astronauts?"
          className={styles.textarea}
          rows={3}
        />

        <div className={styles.topKRow}>
          <label className={styles.label} htmlFor="ask-top-k">
            Passages to retrieve
          </label>
          <input
            id="ask-top-k"
            type="number"
            min={1}
            max={50}
            value={topK}
            onChange={(event) => setTopK(Number(event.target.value))}
            className={styles.topKInput}
          />
        </div>

        <button
          className={styles.button}
          type="submit"
          disabled={loading}
          aria-busy={loading}
        >
          {loading ? "Asking" : "Ask question"}
        </button>
      </form>

      <div className={styles.stateLine} aria-live="polite">
        {loading && "Retrieving evidence and generating a grounded answer."}
        {!loading && error}
        {!loading &&
          !error &&
          searched &&
          !hasAnswer &&
          !isInsufficient &&
          "No answer was returned. Check that the API is running."}
      </div>

      {searched && !loading && !error && isInsufficient && (
        <div className={styles.insufficientBanner} role="status">
          <strong>Insufficient evidence</strong>
          <p>
            {response.sufficiency.reason ??
              "The corpus does not contain enough relevant evidence to answer this question confidently."}
          </p>
          {response.sufficiency.retrieved_chunk_count > 0 && (
            <p className={styles.meta}>
              Retrieved {response.sufficiency.retrieved_chunk_count} passage
              {response.sufficiency.retrieved_chunk_count === 1
                ? ""
                : "s"} from {response.sufficiency.supporting_publication_count}{" "}
              publication
              {response.sufficiency.supporting_publication_count === 1
                ? ""
                : "s"}
              .
            </p>
          )}
        </div>
      )}

      {searched && !loading && !error && hasAnswer && (
        <div className={styles.resultsStack}>
          <section
            className={styles.answerCard}
            aria-labelledby="answer-heading"
          >
            <p className={styles.answerKicker}>Answer</p>
            <h3 id="answer-heading" className={styles.answerHeading}>
              The grounded answer
            </h3>
            <p className={styles.columnHint}>
              This is the generated response. Citation chips such as{" "}
              <code className={styles.inlineCode}>[C1]</code> point to quoted
              passages below.
            </p>
            <CitationLinkedText
              text={response.answer_text}
              activeCitationId={activeCitationId}
              onSelectCitation={setActiveCitationId}
              resolveCitation={resolveCitation}
              className={styles.answerText}
            />
          </section>

          <div className={styles.supportingList}>
            <h3 className={styles.supportingHeading}>Supporting details</h3>

            {hasClaims && (
              <section
                className={styles.claimsSection}
                aria-labelledby="claims-heading"
              >
                <h4 id="claims-heading">Claims</h4>
                <p className={styles.columnHint}>
                  Individual statements split from the answer when the API
                  provides them. These are not paper titles.
                </p>
                <ol className={styles.claimsList}>
                  {response.claims.map((claim) => (
                    <li key={claim.claim_id} className={styles.claimItem}>
                      <p>{claim.text}</p>
                      <div className={styles.claimCitations}>
                        {claim.citation_ids.map((citationId) => (
                          <button
                            key={citationId}
                            type="button"
                            className={styles.citationChip}
                            onClick={() => setActiveCitationId(citationId)}
                            aria-pressed={activeCitationId === citationId}
                            aria-label={`Show evidence for citation ${citationId}`}
                          >
                            {citationId}
                          </button>
                        ))}
                      </div>
                    </li>
                  ))}
                </ol>
              </section>
            )}

            {response.warnings && response.warnings.length > 0 && (
              <section
                className={styles.warningsSection}
                aria-labelledby="warnings-heading"
              >
                <h4 id="warnings-heading">Warnings</h4>
                <ul className={styles.noticeList}>
                  {response.warnings.map((warning) => (
                    <li key={warning.code} className={styles.warningItem}>
                      <strong>{warning.code}:</strong> {warning.message}
                    </li>
                  ))}
                </ul>
              </section>
            )}

            {response.limitations && response.limitations.length > 0 && (
              <section
                className={styles.limitationsSection}
                aria-labelledby="limitations-heading"
              >
                <h4 id="limitations-heading">Limitations</h4>
                <ul className={styles.noticeList}>
                  {response.limitations.map((limitation, index) => (
                    <li key={index} className={styles.limitationItem}>
                      {limitation.text}
                    </li>
                  ))}
                </ul>
              </section>
            )}

            {response.conflicts && response.conflicts.length > 0 && (
              <section
                className={styles.conflictsSection}
                aria-labelledby="conflicts-heading"
              >
                <h4 id="conflicts-heading">Conflicting findings</h4>
                <ul className={styles.noticeList}>
                  {response.conflicts.map((conflict, index) => (
                    <li key={index} className={styles.conflictItem}>
                      {conflict.summary}
                    </li>
                  ))}
                </ul>
              </section>
            )}

            {hasCitations && (
              <section
                className={styles.evidenceCard}
                aria-labelledby="evidence-heading"
              >
                <h4 id="evidence-heading">Cited passages</h4>
                <p className={styles.columnHint}>
                  Quoted text from the indexed PDF. Paper title, publication id,
                  section, and page are listed under each quote.
                </p>
                <EvidencePanel
                  passages={response.citations}
                  activeCitationId={activeCitationId}
                  onSelectCitation={setActiveCitationId}
                  showHeading={false}
                />
              </section>
            )}
          </div>
        </div>
      )}
    </section>
  );
}
