# English source and translation provenance

The pilot uses **Open Music Theory — Fall 2023**, the University of Nebraska
Pressbooks adaptation. The canonical OMT2 project remains
<https://viva.pressbooks.pub/openmusictheory/>. Direct VIVA downloads returned
HTTP 403 during preparation, so no official XML export was obtained.
**The Nebraska edition is not asserted to match current VIVA.**

## What is actually imported

- `catalog.json`: complete table of contents exposed by the Nebraska edition,
  in its own order, including per-entry bylines. It is not the current VIVA TOC.
- `en/*.html`: seven normalized English chapter bodies: introduction, first five
  Fundamentals chapters, and acknowledgments (for authorship/artwork evidence).
  Other chapter bodies have **not** been downloaded or translated.
- `manifest.json`: edition, retrieval date, source URLs and bylines, raw-response
  hashes, normalized-body hashes, excluded cover artwork and media references.
- `translations.json`: each Russian draft's pinned source-body hash and review
  status. Updating the English source never updates this hash automatically.
- `assets.json`: 41 locally retained figures and keyboard photographs with source URLs, hashes,
  attribution and the basis for reuse. Figure 17 comes from the same OMT example
  in LibreTexts because the Nebraska reference points to inaccessible VIVA.

The introduction's adaptation byline says **Brian Moore**. This is retained as
source metadata, not substituted for the seven original OMT2 authors. The five
Fundamentals chapters credit **Chelsey Hamm**.

## Import and compare

From the repository root (Python 3.12+):

```bash
python -m pip install -r scripts/requirements.txt
python scripts/import_upstream.py --output /tmp/omt-candidate
python scripts/diff_upstream.py upstream/manifest.json /tmp/omt-candidate/manifest.json
```

A diff exits 1 for changed/added/removed content, attribution metadata or edition,
0 when unchanged. Review a candidate before copying its snapshots and manifest
into `upstream/`. The importer only reads the explicitly configured source URLs;
there is no automatic publication or automatic translation rewrite.

Downloads are cached under `.cache/omt/` (ignored by Git). To normalize an existing
cache, supply its **actual retrieval date**, not today's date unless fetched today:

```bash
python scripts/import_upstream.py --offline --retrieved-at 2026-09-20 --output /tmp/omt-candidate
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
