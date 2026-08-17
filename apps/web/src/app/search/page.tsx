import Image from "next/image";
import Link from "next/link";

import { SearchClient } from "./SearchClient";
import styles from "./search.module.css";

export default function SearchPage() {
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
        <h1 className={styles.heading}>Search</h1>
        <p className={styles.lede}>
          Query stored publication metadata and any exposed passage records while
          keeping publication IDs, source links, sections, and pages visible.
        </p>
      </header>

      <SearchClient />
    </main>
  );
}
