import Image from "next/image";
import Link from "next/link";

import corpus from "@/data/corpus.json";
import { type CorpusPublication } from "@/data/corpus";

import { CompareClient } from "./CompareClient";
import styles from "./compare.module.css";

const publications = corpus as CorpusPublication[];

export const metadata = {
  title: "Compare studies",
};

export default function ComparePage() {
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
        <Link href="/" className={styles.brand}>
          <Image
            src="/brand/logo-wordmark.png"
            alt="Space Biology Evidence Engine"
            width={280}
            height={80}
            className={styles.wordmark}
            priority
          />
        </Link>
        <h1 className={styles.heading}>Compare studies</h1>
        <p className={styles.lede}>
          Place corpus inventory records side by side. Organism and system
          categories stay labeled. This page does not synthesize unstated
          findings.
        </p>
        <p className={styles.navRow}>
          <Link href="/corpus">Corpus</Link>
          <Link href="/ask">Ask</Link>
        </p>
      </header>
      <CompareClient publications={publications} />
    </main>
  );
}
