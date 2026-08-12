# Web app (`apps/web`)

Next.js TypeScript scaffold for the citation-first UI.

```bash
# from repo root
make web
# http://localhost:3000
```

Ask / citation screens land on later web-interface issues. The reusable
`EvidencePanel` and citation-link helpers (`CitationLinkedText`,
`AnswerEvidenceView`) under `src/components/evidence` are ready for the
question-answering page (#62) to mount cited answers.
