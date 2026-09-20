# Python tooling

Requires **Python 3.12+**. The four existing commands and their arguments remain:

```bash
python -m pip install -r scripts/requirements.txt
python scripts/import_upstream.py --output /tmp/omt-candidate
python scripts/diff_upstream.py upstream/manifest.json /tmp/omt-candidate/manifest.json
python scripts/render_glossary.py --check
python scripts/check_book.py --built
```

The entry files parse arguments and report results. Typed processing lives in the
local `omt` package; no package installation, server or framework is required.
Russian text and editorial review status are never automatically rewritten.

## Where to read or change the code

| Module | Responsibility |
|---|---|
| `omt/models.py` | Pydantic schemas for configuration, manifests, translations, assets, catalog and glossary; duplicate-key checks |
| `omt/files.py` | UTF-8 input, field-level validation errors, SHA-256, JSON encoding and single-file replacement |
| `omt/pressbooks.py` | Source-specific HTML extraction, v1 normalization, media discovery and nested TOC parsing |
| `omt/importing.py` | Download/cache access, preparation of an entire import, then explicit output writing |
| `omt/comparison.py` | Pure manifest comparison returning a named `ManifestDiff` |
| `omt/glossary.py` | Pure `Glossary` → Markdown rendering |
| `omt/validation.py` | Separate checks for source snapshots, translation bindings and assets |
| `omt/html_checks.py` | Built-page links, cached target anchors and accessibility labels |
| `omt/cli.py` | Expected input/I/O failures → a readable stderr message and exit code 2 |

For example, to change glossary formatting, edit `render_term()` or `render()`;
to change the treatment of an HTML element, edit `normalize_markup()`; to add a
provenance rule, add it to the relevant validator. The extractor returns an
`ExtractedChapter` dataclass instead of an unnamed tuple. File schemas are checked
when read, so processing code uses attributes rather than unstructured dictionaries.

Pydantic models cover stored records. Small in-memory results use standard-library
dataclasses. URLs and timestamps remain strings to preserve their recorded spelling;
these schemas do not establish URL availability or validate every editorial rule.
XPath element selection has one explicit cast at the lxml boundary; callers use
only expressions selecting HTML elements, never scalar XPath expressions.

## Dependency decisions for review

| Choice | Reason / tradeoff |
|---|---|
| Add Pydantic 2.13.5 | Typed schemas, nested validation, explicit statuses and useful field paths. Strict validation and forbidden extra fields replace scattered dictionary assumptions. Adds the compiled pydantic-core dependency and typing/annotation helpers. |
| Keep lxml 6.1.1 | Already handles Pressbooks HTML and XPath. Replacing the parser could change snapshot bytes and hashes. |
| Keep PyYAML 6.0.3 | `safe_load` remains the YAML parser; its result is validated as a `Glossary`. |
| Keep argparse and urllib | Existing small CLI and synchronous downloads need no additional CLI or HTTP framework. The downloader has a 45-second timeout and is isolated for tests. |
| Add Ruff and mypy to development requirements | Formatting, lint and strict type checks are reproducible CI gates. The Pydantic mypy plugin checks model construction. |
| Add types-PyYAML and types-lxml to development requirements | Check third-party API usage without global missing-import suppression. The lxml stub package brings additional development dependencies, including Beautiful Soup and cssselect; they are not runtime choices for our code. |
| Keep unittest | Existing tests need no new runner; mocks and subprocess tests cover the relevant boundaries. |

Direct dependencies are pinned in the two requirements files. They are not a full
transitive lockfile. Deploy installs runtime requirements only; PR/push Test CI
installs development requirements. No dependency is loaded from an unpinned Git branch.

References: [Pydantic models](https://docs.pydantic.dev/latest/concepts/models/),
[Pydantic strict mode](https://docs.pydantic.dev/latest/concepts/strict_mode/),
[mypy strict mode](https://mypy.readthedocs.io/en/stable/command_line.html#cmdoption-mypy-strict).

## Compatibility and intentional changes

- Command names, options, file locations and valid JSON/YAML shapes are preserved.
  Normalizer version remains 1. The refactor was compared against the old importer
  using all seven available cached source pages: every normalized HTML snapshot,
  `catalog.json` and `manifest.json` was byte-identical for the same retrieval date.
  The committed rendered glossary is also byte-identical. Raw downloads remain
  ignored cache files; the seven-page comparison requires that local cache.
- A committed small HTML fixture and its pre-refactor normalized output provide
  a portable normalization regression test. Existing importer scenarios are
  retained; additional tests exercise schemas, comparison, rendering, links and CLI behavior.
- Missing/malformed fields, unknown fields, incorrect types, invalid SHA-256
  strings, duplicate record IDs/paths/terms and an empty source configuration
  now fail explicitly. Previously some failed with tracebacks or were silently
  collapsed by dictionary construction. Intentional schema extensions must update
  the models and tests together.
- Diff still exits 0 when unchanged and 1 when changed. Glossary/book checks still
  exit 1 for a failed check. Expected input, parsing or I/O failures exit 2 with
  diagnostics; missing CLI arguments also exit 2. Unexpected programming errors
  retain tracebacks. Internal Python APIs now accept and return typed objects;
  the command-line interface is the compatibility boundary.
- Online import extracts each chapter once. All pages are prepared before source
  output changes. Each file is replaced through a temporary file in the same
  directory, with the manifest written last. **This is not an atomic multi-file
  transaction**: disk failure during publication can leave mixed revisions. Keep
  importing to a candidate directory and reviewing it before adoption.

## Remaining limits

An old offline cache records HTML but not HTTP redirect metadata, so offline
imports use the configured URL. The catalog still comes from the first configured
page. Manifest comparison does not compare catalog changes or show textual diffs.
Do not alter these behaviors silently as part of a formatting refactor.

Normalized source HTML is archival input, not a general-purpose sanitized web
page. It stays outside `src/`. The built-book checker checks local links and the
presence of labels, not translation accuracy, label quality, external playback or
human-review evidence. Those remain in the documented editorial workflow.

## Working on the scripts

From the repository root:

```bash
python -m pip install -r scripts/requirements-dev.txt
ruff check scripts tests
ruff format --check scripts tests
mypy
python -m unittest discover -s tests -v
python scripts/render_glossary.py --check
python scripts/check_book.py
mdbook build
python scripts/check_book.py --built
```

Use `ruff format scripts tests` to format changes before checking. mypy is strict
for both production scripts and tests. The same formatting, lint, type and test
commands run in Test CI.

Suggested review order: models → extraction/import orchestration → comparison and
rendering → validators → CLI wrappers → tests and dependency/CI changes. Pay
particular attention to schema strictness, unchanged normalization bytes and the
limited guarantees of per-file atomic writes.
