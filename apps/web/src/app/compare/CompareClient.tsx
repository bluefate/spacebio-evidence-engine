"use client";

import { useMemo, useState } from "react";
import Link from "next/link";

import {
  buildComparison,
  organismSystemCategory,
} from "@/data/compare";
import { formatLabel, type CorpusPublication } from "@/data/corpus";

import { NewTabLink } from "@/components/a11y/NewTabLink";

import styles from "./compare.module.css";

type CompareClientProps = {
  publications: CorpusPublication[];
};

export function CompareClient({ publications }: CompareClientProps) {
  const [selectedIds, setSelectedIds] = useState<string[]>([]);

  const selected = useMemo(
    () => publications.filter((item) => selectedIds.includes(item.id)),
    [publications, selectedIds],
  );
  const rows = useMemo(() => buildComparison(selected), [selected]);
  const ready = selected.length >= 2;

  function toggle(id: string) {
    setSelectedIds((current) =>
      current.includes(id) ? current.filter((item) => item !== id) : [...current, id],
    );
  }

  return (
    <div className={styles.layout}>
      <p className={styles.disclaimer} role="note">
        Comparison uses corpus inventory metadata only (organism, exposure, notes).
        It does not retrieve passages, generate findings, or invent differences that
        are not present in those fields. Organism classes stay labeled and are not
        merged.
      </p>

      <section className={styles.picker} aria-labelledby="compare-select-heading">
        <h2 id="compare-select-heading" className={styles.sectionHeading}>
          Select publications
        </h2>
        <p className={styles.hint}>Choose at least two records to compare.</p>
        <ul className={styles.pickerList}>
          {publications.map((pub) => {
            const inputId = `compare-pub-${pub.id}`;
            const checked = selectedIds.includes(pub.id);
            return (
              <li key={pub.id}>
                <label className={styles.pickerItem} htmlFor={inputId}>
                  <input
                    id={inputId}
                    type="checkbox"
                    checked={checked}
                    onChange={() => toggle(pub.id)}
                  />
                  <span className={styles.pickerBody}>
                    <span className={styles.pickerId}>{pub.id}</span>
                    <span className={styles.pickerTitle}>{pub.title}</span>
                    <span className={styles.pickerMeta}>
                      {organismSystemCategory(pub.organism)} ·{" "}
                      {formatLabel(pub.organism)} · {formatLabel(pub.exposure)}
                    </span>
                  </span>
                </label>
              </li>
            );
          })}
        </ul>
      </section>

      {!ready ? (
        <p className={styles.emptyState}>
          Select two or more publications to open the comparison table.
        </p>
      ) : (
        <section className={styles.tableWrap} aria-labelledby="compare-table-heading">
          <h2 id="compare-table-heading" className={styles.sectionHeading}>
            Side-by-side inventory comparison
          </h2>
          <div className={styles.tableScroll}>
            <table className={styles.table}>
              <caption className="visuallyHidden">
                Inventory fields for {selected.length} selected publications
              </caption>
              <thead>
                <tr>
                  <th scope="col">Field</th>
                  {selected.map((pub) => (
                    <th key={pub.id} scope="col">
                      <Link href={`/publications/${pub.id}`}>{pub.id}</Link>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.map((row) => (
                  <tr
                    key={row.field}
                    data-differs={row.differs ? "true" : "false"}
                    className={row.differs ? styles.differs : undefined}
                  >
                    <th scope="row">{row.label}</th>
                    {row.values.map((value, index) => (
                      <td key={`${row.field}-${selected[index].id}`}>{value}</td>
                    ))}
                  </tr>
                ))}
                <tr>
                  <th scope="row">Source</th>
                  {selected.map((pub) => (
                    <td key={`src-${pub.id}`}>
                      <NewTabLink href={pub.sourceUrl}>Open DOI</NewTabLink>
                    </td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      )}
    </div>
  );
}
