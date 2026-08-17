import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";

import corpus from "@/data/corpus.json";
import {
  formatLabel,
  formatLicense,
  type CorpusPublication,
} from "@/data/corpus";

import { NewTabLink } from "@/components/a11y/NewTabLink";

import styles from "./publication-detail.module.css";

const publications = corpus as CorpusPublication[];

function getPublication(id: string): CorpusPublication | undefined {
  return publications.find((publication) => publication.id === id);
}

function DetailRow({
  label,
  value,
}: {
  label: string;
  value: React.ReactNode;
}) {
  return (
    <div className={styles.detailRow}>
      <dt>{label}</dt>
      <dd>{value}</dd>
    </div>
  );
}

function ExternalLink({ href, children }: { href: string; children: string }) {
  return (
    <NewTabLink className={styles.externalLink} href={href}>
      {children}
    </NewTabLink>
  );
}

export function generateStaticParams() {
  return publications.map((publication) => ({ id: publication.id }));
}

type PublicationPageProps = {
  params: Promise<{ id: string }>;
};

export async function generateMetadata({ params }: PublicationPageProps) {
  const { id } = await params;
  const publication = getPublication(id);

  return {
    title: publication
      ? `${publication.id}: ${publication.title}`
      : "Publication not found",
  };
}

export default async function PublicationDetailPage({
  params,
}: PublicationPageProps) {
  const { id } = await params;
  const publication = getPublication(id);

  if (!publication) {
    notFound();
  }

  const sections = publication.sections ?? [];
  const chunks = publication.chunks ?? [];

  return (
    <main id="main-content" className={styles.page} tabIndex={-1}>
      <div className={styles.heroBackdrop} aria-hidden>
        <Image
          src="/brand/hero-atmosphere.png"
          alt=""
          fill
          priority
          className={styles.heroImage}
          sizes="100vw"
        />
      </div>

      <header className={styles.header}>
        <Link href="/corpus" className={styles.backLink}>
          Back to corpus
        </Link>
        <div className={styles.kicker}>{publication.id}</div>
        <h1 className={styles.heading}>{publication.title}</h1>
        <div className={styles.badges}>
          <span className={`${styles.badge} ${styles.accent}`}>{publication.year}</span>
          <span className={`${styles.badge} ${styles.license}`}>
            {formatLicense(publication.license)}
          </span>
          <span className={styles.badge}>{formatLabel(publication.organism)}</span>
          <span className={styles.badge}>{formatLabel(publication.exposure)}</span>
        </div>
      </header>

      <section className={styles.panel} aria-labelledby="publication-metadata">
        <h2 id="publication-metadata">Publication Metadata</h2>
        <dl className={styles.details}>
          <DetailRow label="Publication ID" value={publication.id} />
          <DetailRow label="Title" value={publication.title} />
          <DetailRow label="DOI" value={publication.doi} />
          <DetailRow label="Year" value={publication.year} />
          <DetailRow label="License" value={formatLicense(publication.license)} />
          <DetailRow label="Organism" value={formatLabel(publication.organism)} />
          <DetailRow label="Exposure" value={formatLabel(publication.exposure)} />
          <DetailRow label="Corpus note" value={publication.notes} />
          <DetailRow label="Approval status" value={formatLabel(publication.approval)} />
          <DetailRow label="Ingestion status" value={formatLabel(publication.ingestion)} />
        </dl>
      </section>

      <section className={styles.panel} aria-labelledby="source-provenance">
        <h2 id="source-provenance">Source And Provenance</h2>
        <dl className={styles.details}>
          <DetailRow
            label="Original publication"
            value={
              <ExternalLink href={publication.sourceUrl}>
                Open publisher DOI page
              </ExternalLink>
            }
          />
          <DetailRow
            label="Stored source URL"
            value={
              <ExternalLink href={publication.sourceUrl}>
                {publication.sourceUrl}
              </ExternalLink>
            }
          />
          <DetailRow
            label="Stored PDF URL"
            value={<ExternalLink href={publication.pdfUrl}>{publication.pdfUrl}</ExternalLink>}
          />
        </dl>
      </section>

      <section className={styles.panel} aria-labelledby="sections-chunks">
        <h2 id="sections-chunks">Sections And Chunks</h2>
        <div className={styles.summaryGrid}>
          <div>
            <span className={styles.summaryValue}>{sections.length}</span>
            <span className={styles.summaryLabel}>stored sections</span>
          </div>
          <div>
            <span className={styles.summaryValue}>{chunks.length}</span>
            <span className={styles.summaryLabel}>stored chunks</span>
          </div>
        </div>
        {sections.length > 0 ? (
          <ul className={styles.sectionList}>
            {sections.map((section) => (
              <li key={section}>{section}</li>
            ))}
          </ul>
        ) : (
          <p className={styles.emptyState}>
            No section or chunk summaries are available in the stored publication
            metadata for this record.
          </p>
        )}
      </section>
    </main>
  );
}
