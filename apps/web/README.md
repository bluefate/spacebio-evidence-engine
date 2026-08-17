# Web app (`apps/web`)

Next.js TypeScript scaffold for the citation-first UI.

```bash
# from repo root
make web
# http://localhost:3000

make test-web
# or: cd apps/web && npm test
```

Citation and answer UI tests live next to the components:

- `src/app/ask/AskClient.test.tsx`
- `src/components/evidence/CitationLinks.test.tsx`
- `src/components/evidence/EvidencePanel.test.tsx`

See [TESTING_STRATEGY.md](../../docs/development/TESTING_STRATEGY.md).
