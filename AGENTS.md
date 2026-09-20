# Translation work in this repository

Read `CONTRIBUTING.md`, `docs/translation-policy.md`, `docs/chapter-tracker.md`,
`src/translation-notes.md` and `glossary/terminology.yml` before translation work.
For a limited documentation or code change, read the portions relevant to it.

- Check current repository state and open PRs before choosing the next batch.
  Follow the user's established access method; GitHub work in this project uses
  the connector. Do not switch to browser access without authorization.
- Use the explicitly dated Nebraska Fall 2023 baseline. Do not mix editions or
  claim current-VIVA equivalence. Import English candidates separately; never
  overwrite Russian text or advance source bindings without comparison.
- For each new translation, keep a completed `docs/reviews/<source-id>.md` record
  based on `docs/chapter-checklist.md`, including element inventory, deviations,
  review evidence and remaining work. Update the chapter tracker in the same PR.
- Preserve attribution and distinguish source text from translator additions.
  Use the YAML glossary as the terminology source; regenerate its rendered page.
- Separate technical checks, AI comparison, human review and media localization.
  Do not invent reviewers, retroactively certify earlier work, or promote draft
  status because CI passes or Pages deploys. Record unavailable checks honestly.
- Keep batches reviewable, normally 1–3 related chapters. Routine implementation
  choices do not need new confirmation. Independent human review is not required
  to prepare a clearly labeled draft PR; unresolved material errors are recorded
  against the affected chapter while other work can continue.
- Use the existing validation commands and the PR template. For documentation
  changes, verify affected links and records; do not add tests that merely mirror
  prose. Add regression coverage when fixing an actual importer defect.

These are repository contribution instructions, not an installable skill.

For Python changes, read `scripts/README.md`, run `uv sync --locked`, and use
`uv run --locked` for Ruff lint/format checks, strict mypy and the tests. Keep
dependencies in `pyproject.toml` and commit `uv.lock` with dependency changes.
Keep dependency and behavior changes explicit in the PR. Preserve
normalizer output unless an intentional source-format migration is in scope.
