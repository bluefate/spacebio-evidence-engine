import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";

import { isRetrievalDiagnosticsEnabled } from "@/config/devFlags";

import styles from "../../ask/ask.module.css";
import { RetrievalDiagnosticsClient } from "./RetrievalDiagnosticsClient";

export default function RetrievalDiagnosticsPage() {
  if (!isRetrievalDiagnosticsEnabled()) {
    notFound();
  }

  return (
    <main className={styles.page}>
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
        <h1 className={styles.heading}>Retrieval diagnostics</h1>
        <p className={styles.lede}>
          Inspect retrieval inputs as a query hash plus selected chunk IDs, scores, and citation
          IDs. This page is off unless NEXT_PUBLIC_ENABLE_RETRIEVAL_DIAGNOSTICS is enabled.
        </p>
      </header>

      <RetrievalDiagnosticsClient />
    </main>
  );
}
