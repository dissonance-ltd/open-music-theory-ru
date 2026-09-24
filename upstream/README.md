# English source and translation provenance

The pilot uses **Open Music Theory — Fall 2023**, the University of Nebraska
Pressbooks adaptation. The canonical OMT2 project remains
<https://viva.pressbooks.pub/openmusictheory/>. Direct VIVA downloads returned
HTTP 403 during preparation, so no official XML export was obtained.
**The Nebraska edition is not asserted to match current VIVA.**

## What is actually imported

- `catalog.json`: complete table of contents exposed by the Nebraska edition,
  in its own order, including per-entry bylines. It is not the current VIVA TOC.
  There are 136 entries including 116 chapter links. Unlinked section headings
  use `url: null` and retain their children; this preserves the Workbook heading
  and its Digital/PDF Workbook links, previously skipped by the importer.
  Catalog membership does not establish body availability or media completeness.
  Editorial progress and the full inventory are in [the chapter tracker](../docs/chapter-tracker.md).
- `en/*.html`: twenty normalized English chapter bodies: introduction, first eighteen
  Fundamentals chapters, and acknowledgments (for authorship/artwork evidence).
  This branch includes batches 04 (chapters 9–11), 05 (chapters 12–14), 06 (chapters 15–17), and 07 (chapter 18).
  Remaining chapter bodies have not been assessed.
- `manifest.json`: edition, retrieval date, source URLs and bylines, raw-response
  hashes, normalized-body hashes, excluded cover artwork and media references.
- `translations.json`: each Russian draft's pinned source-body hash and review
  status. Updating the English source never updates this hash automatically.
- `assets.json`: 95 locally retained figures and keyboard photographs with source URLs, hashes,
  attribution and the basis for reuse. Figure 17 comes from the same OMT example
  in LibreTexts because the Nebraska reference points to inaccessible VIVA.

The introduction's adaptation byline says **Brian Moore**. This is retained as
source metadata, not substituted for the seven original OMT2 authors. Fundamentals chapters 1–5 credit **Chelsey Hamm**; chapter 6 credits
**Chelsey Hamm and Bryn Hughes**, chapter 7 **Chelsey Hamm and Mark Gotham**,
chapter 8 **Chelsey Hamm, Mark Gotham and Bryn Hughes**, chapter 9
**Chelsey Hamm, Kris Shaffer and Mark Gotham**, chapter 10 **Chelsey Hamm and Mark Gotham**,
chapter 11 **Bryn Hughes, Mark Gotham and Chelsey Hamm**, chapters 12–13
**Chelsey Hamm and Bryn Hughes**, chapter 14 **Chelsey Hamm**, chapter 15
**Kris Shaffer, Chelsey Hamm and Samuel Brady**, chapter 16 **Chelsey Hamm and Bryn Hughes**,
and chapters 17–18 **Chelsey Hamm**.

## Import and compare

From the repository root with uv (Python 3.12 is selected in `.python-version`):

```bash
uv sync --locked
uv run --locked python scripts/import_upstream.py --output /tmp/omt-candidate
uv run --locked python scripts/diff_upstream.py upstream/manifest.json /tmp/omt-candidate/manifest.json
```

A diff exits 1 for changed/added/removed content, attribution metadata or edition,
0 when unchanged. Review a candidate before copying its snapshots and manifest
into `upstream/`. The importer only reads the explicitly configured source URLs;
there is no automatic publication or automatic translation rewrite.

Downloads are cached under `.cache/omt/` (ignored by Git). To normalize an existing
cache, supply its **actual retrieval date**, not today's date unless fetched today:

```bash
uv run --locked python scripts/import_upstream.py --offline --retrieved-at 2026-09-20 --output /tmp/omt-candidate
```

The normalizer removes site navigation, headers (bylines are retained in the
manifest), scripts, styles, event handlers, reserved cover/logo references and
interactive glossary buttons. It retains text, glossary definitions, links,
figure references and iframe URLs in English source HTML. It does not convert
that HTML into Russian or silently discard unsupported exercises. English HTML
is archival input outside mdBook's `src/` and is not published as a site page.

## Media and adaptation limits

The page-level CC BY-SA 4.0 notice applies except where otherwise noted. The
acknowledgments reserve Bethany Nistler's cover/logo artwork; neither is copied.
The local notation figures have no separate restrictive notice in the source
chapter. Source captions/alt descriptions are translated; labels inside the
figures remain English. The original introduction's cover and illustrative
interface screenshots are omitted from the Russian page and that omission is
explicit there.

Third-party video and worksheets remain external references. Their bytes are
not mirrored and are not relicensed by this repository. All worksheet links are
retained, but their availability and contents have not been exhaustively audited.
The video has a direct-link fallback; playback may depend on the user's location
and browser. No complete H5P migration or current-VIVA synchronization is claimed.

Further draft batches continue against the explicitly dated Nebraska adaptation.
Before presenting this as a translation of current VIVA, obtain an accessible
current official source, compare editions, and retain per-chapter revision
history. Never relabel the 2023 snapshot as current.

## Second batch: source repairs and translation choices

- Reading Clefs retains English mnemonic phrases with Russian note sequences and
  an explanation of why literal translation would lose the initial letters.
- The Keyboard and the Grand Staff contains a malformed, escaped image tag for
  example 8. Its referenced Nebraska image was recovered by changing the Unicode
  multiplication sign in the filename to ASCII `x`. The image was visually checked
  against the adjacent examples and caption. Both URLs and the downloaded hash
  are in `assets.json`; the archived source HTML retains the original defect.
- `generic interval` is rendered as «ступеневая величина интервала», distinguished
  from counting semitones. Other marked translator notes explain middle C,
  equal temperament, accidental reference pitch and octave-boundary spellings.
- Reading Clefs labels two MuseScore links `.mscx` although their URLs end in
  `.mscz#fixme`. Translated labels follow the URL; original URLs are retained
  and their availability remains unverified.
- New external videos retain accessible titles and direct YouTube links. No
  external video, application or worksheet availability audit is claimed.

## Third batch: parallel translation pilot

Only chapters 6–8 were fetched for this batch, at
`2026-09-20T22:26:27.379624+00:00`. The seven previously accepted snapshots and
the catalog are unchanged; the newly fetched catalog compared equal. The combined
manifest uses the common actual UTC retrieval day, `2026-09-20`, instead of
applying the previous batch's precise timestamp to new downloads. Exact pilot
retrieval times and source hashes are recorded in the three chapter review records.
No existing translation source binding is advanced.

Thirteen original figures were retained locally. Internal image text is unchanged;
Russian captions and alt text are supplied. Other Notation examples 3–7 and 9–11
have explanatory text but no corresponding media in either the raw response or
the normalized snapshot. Rhythm contains a missing-table-74 message. These source
defects remain in the English archive and are visibly disclosed in the Russian
drafts, together with limited corrections to misleading definitions. External
MuseScore examples are now embedded with permanent source links; worksheets remain links. Neither is newly localized or certified by this presentation change.

See the [batch workflow](../docs/batch-translation.md) and chapter records for
[ASPN](../docs/reviews/aspn.md), [Other Notation](../docs/reviews/other-notation.md),
and [Rhythmic Values](../docs/reviews/rhythmic-rest-values.md).

## Fourth batch: meter and other rhythmic essentials

Chapters 9–11 were retrieved at `2026-09-20T23:02:37.155996+00:00`.
The ten previously accepted snapshots and existing source bindings are retained.
At that stage, all snapshots shared the UTC retrieval day `2026-09-20`.
Exact chapter timestamps and hashes remain recorded in the chapter reviews;
see the batch 06 note below for the later retrieval cohort.

Eleven source figures were added: nine for Simple Meter and two for Compound Meter.
Other Rhythmic Essentials contains no embedded figures in either its raw HTML or
normalized snapshot: all four examples are external MuseScore links. Simple Meter
examples 5–7 and Compound Meter table 36 are absent from the source and explicitly
marked in the translation. Misleading definitions and the flag-direction statement
are addressed in visible translator notes, without editing the English snapshots.

A separate AI comparison has been performed for all three chapters; findings and
correction checks are retained in their records. Human review, rendered-page review,
external-content inspection and playback checks remain pending. Technical results
are recorded in the chapter records and batch PR. See [Simple Meter](../docs/reviews/simple-meter.md),
[Compound Meter](../docs/reviews/compound-meter.md), and
[Other Rhythmic Essentials](../docs/reviews/rhythmic-essentials.md).

Batch 05 (chapters 12–14) was originally prepared concurrently and stacked on batch 04.
Its original PR #8 was merged into that branch after batch 04 had reached main,
leaving chapters 12–14 absent from main. [PR #10](https://github.com/dissonance-ltd/open-music-theory-ru/pull/10)
restores the unchanged chapter content and review evidence to main.

## Fifth batch: scales, key signatures and modes

Chapters 12–14 were retrieved at `2026-09-20T23:02:37.621733+00:00`.
The thirteen earlier snapshots and their translation source bindings are retained.
Fifteen original figures were added: ten for Major Scales, four for Minor Scales
and one for Modes. At the end of batch 05, the collection contained 79 Nebraska figures and the
earlier LibreTexts copy of Notation example 17. Internal labels remain unchanged;
Russian captions and alt descriptions are supplied.

Major Scales table 37, Minor Scales tables 39/40 and examples 10/11 are absent
from the source. Empty or corrupted popup definitions in Minor Scales and Modes
are disclosed rather than reconstructed as source text. Marked translator notes
explain corrections and terminology choices; the English archive is unchanged.
External scores, worksheets, video and audio remain unverified, unlocalized links.

Separate AI comparisons are complete for all three chapters; targeted corrections
and their verification are recorded in [Major Scales](../docs/reviews/major-scales.md),
[Minor Scales](../docs/reviews/minor-scales.md), and [Modes](../docs/reviews/modes.md).
Technical results are recorded there and in the batch PR. Human review, rendered-page
review and external-content/playback checks remain pending. All translations
retain draft status; merging either batch does not certify editorial completion.


## Sixth batch: sight-singing, intervals and triads

Chapters 15–17 were retrieved at `2026-09-23T10:21:40.881030+00:00`.
The sixteen earlier snapshots and source bindings remain unchanged. The new catalog
compared equal to the retained catalog. Schema v1 has only a global `manifest.retrieved_at`: its retained value
`2026-09-20` is the legacy baseline retrieval date, not the retrieval date of all
chapters. The actual timestamp for chapters 15–17 is recorded in their review
records and the per-cohort [retrieval ledger](retrievals.json). Earlier cohort
timestamps remain as documented above; the new date does not relabel those downloads.
This translation batch does not change the importer or manifest schema.

Twelve original Nebraska figures were added: three for Sight-Singing, five for Intervals,
and four for Triads. The collection now contains 19 English snapshots, 18 Russian drafts,
and 92 local figures (91 from Nebraska and one from LibreTexts). Figure captions and
alt descriptions are Russian; the original image content is unchanged.

Sight-Singing examples 9–11 are missing and example number 4 is repeated. Intervals
tables 61, 63, and 64 are absent. Broken popup definitions, including unrelated chapter
content in Intervals and Triads, are inventoried and disclosed in the Russian drafts;
missing definitions are not reconstructed by guesswork. The English snapshots are unchanged.
See [Sight-Singing](../docs/reviews/sight-singing.md), [Intervals](../docs/reviews/intervals.md),
and [Triads](../docs/reviews/triads.md) for exact inventories and deviations.

Separate AI reviews are complete: `review_batch06_singing_triads` for chapters 15/17,
`review_batch06_intervals` for chapter 16 and cross-chapter terminology. Their findings and rechecks are recorded per chapter, including the closed
Intervals clarification and a review of all 47 new glossary entries. Technical results
belong to the records and PR. Human review, rendered-page/mobile review, external-content inspection and
per-score playback checks remain pending. On 2026-09-23 the user confirmed that the
MuseScore pilot works and requested rollout. All 60 source scores in chapters 6–17
are now embedded, with permanent direct links. See the [inventory and rules](../docs/musescore-embeds.md).

PR #10 restored batch 05 into main. PR #11 was merged into the old restoration
branch, so this MuseScore rollout PR brings the already-reviewed batch 06 into main
as a separate prerequisite commit. This PR targets main directly. Subsequent work
begins with chapter 18; no translator is assigned yet.

## Seventh batch: seventh chords

Chapter 18 was retrieved from the Nebraska Fall 2023 page at `2026-09-23T16:48:26.033079+00:00` via GitHub Actions run 35891273758 (artifact 10764632374). The v1 importer normalized its raw response offline without changing the 19 existing snapshots; the source catalog compared equal. The legacy global manifest date remains the baseline date; the new per-cohort entry is in `retrievals.json`. Three original Nebraska images were fetched at full available resolution and indexed with source references and SHA-256 in `assets.json`. Table 73 is absent from the source; example numbering conflicts and damaged popup definitions are described in [the chapter record](../docs/reviews/seventh-chords.md). Third-party media and worksheets remain English and unverified.
