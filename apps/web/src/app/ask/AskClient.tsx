"use client";

import { FormEvent, useState } from "react";

import { EvidencePanel } from "@/components/evidence";
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
  const [question, setQuestion] = useState("");
  const [topK, setTopK] = useState(8);
  const [response, setResponse] = useState<GroundedAnswerResponse>(emptyResponse);
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

  return (
    <section className={styles.askPanel} aria-labelledby="ask-heading">
      <div className={styles.panelHeader}>
        <h2 id="ask-heading">Grounded question</h2>
        <p className={styles.helpText}>
          Answers are generated from retrieved corpus passages and include citations so you can
          verify every claim.
        </p>
      </div>

      <form className={styles.askForm} onSubmit={onSubmit}>
        <label className={styles.label} htmlFor="ask-question">
          Research question
        </label>
        <textarea
          id="ask-question"
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

        <button className={styles.button} type="submit" disabled={loading}>
          {loading ? "Asking" : "Ask question"}
        </button>
      </form>

      <div className={styles.stateLine} aria-live="polite">
        {loading && "Retrieving evidence and generating a grounded answer."}
        {!loading && error}
        {!loading && !error && searched && !hasAnswer && !isInsufficient &&
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
              {response.sufficiency.retrieved_chunk_count === 1 ? "" : "s"} from{" "}
              {response.sufficiency.supporting_publication_count} publication
              {response.sufficiency.supporting_publication_count === 1 ? "" : "s"}.
            </p>
          )}
        </div>
      )}

      {searched && !loading && !error && hasAnswer && (
        <div className={styles.answerLayout}>
          <section className={styles.answerColumn} aria-labelledby="answer-heading">
            <h3 id="answer-heading">Answer</h3>
            <p className={styles.answerText}>{response.answer_text}</p>

            {hasClaims && (
              <div className={styles.claimsSection}>
                <h4>Claims and citations</h4>
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
                          >
                            {citationId}
                          </button>
                        ))}
                      </div>
                    </li>
                  ))}
                </ol>
              </div>
            )}

            {response.warnings && response.warnings.length > 0 && (
              <div className={styles.warningsSection}>
                <h4>Warnings</h4>
                <ul className={styles.noticeList}>
                  {response.warnings.map((warning) => (
                    <li key={warning.code} className={styles.warningItem}>
                      <strong>{warning.code}:</strong> {warning.message}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {response.limitations && response.limitations.length > 0 && (
              <div className={styles.limitationsSection}>
                <h4>Limitations</h4>
                <ul className={styles.noticeList}>
                  {response.limitations.map((limitation, index) => (
                    <li key={index} className={styles.limitationItem}>
                      {limitation.text}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {response.conflicts && response.conflicts.length > 0 && (
              <div className={styles.conflictsSection}>
                <h4>Conflicting findings</h4>
                <ul className={styles.noticeList}>
                  {response.conflicts.map((conflict, index) => (
                    <li key={index} className={styles.conflictItem}>
                      {conflict.summary}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </section>

          {hasCitations && (
            <section className={styles.evidenceColumn} aria-labelledby="evidence-heading">
              <h3 id="evidence-heading">Evidence</h3>
              <EvidencePanel
                passages={response.citations}
                activeCitationId={activeCitationId}
                onSelectCitation={setActiveCitationId}
                heading="Cited passages"
              />
            </section>
          )}
        </div>
      )}
    </section>
  );
}
