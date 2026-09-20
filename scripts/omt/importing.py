"""Download/cache orchestration and explicit publication of a prepared import."""

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from urllib.request import urlopen

from lxml import html

from .files import InputError, sha256, write_bytes, write_json
from .models import Catalog, SourceChapter, SourceConfig, SourceManifest, SourcePage
from .pressbooks import extract_catalog, extract_chapter

DOWNLOAD_TIMEOUT_SECONDS = 45


@dataclass(frozen=True)
class PageResponse:
    content: bytes
    resolved_url: str


@dataclass(frozen=True)
class PreparedImport:
    manifest: SourceManifest
    catalog: Catalog
    snapshots: dict[str, bytes]


def download_page(url: str) -> PageResponse:
    with urlopen(url, timeout=DOWNLOAD_TIMEOUT_SECONDS) as response:
        return PageResponse(response.read(), response.url)


def load_page(page: SourcePage, cache: Path, *, offline: bool) -> PageResponse:
    if offline:
        # Legacy cache files contain raw HTML only, without redirect metadata.
        return PageResponse((cache / f"{page.id}.html").read_bytes(), page.url)
    return download_page(page.url)


def prepare_import(
    config: SourceConfig,
    cache: Path,
    *,
    offline: bool = False,
    retrieved_at: str | None = None,
) -> PreparedImport:
    """Parse every page before modifying any published source snapshot."""
    if offline and not retrieved_at:
        raise InputError("--offline requires --retrieved-at (the actual cache retrieval date)")

    chapters = []
    snapshots = {}
    catalog: Catalog | None = None
    for page in config.pages:
        response = load_page(page, cache, offline=offline)
        document = html.fromstring(response.content)
        extracted = extract_chapter(document, response.resolved_url)
        if catalog is None:
            catalog = Catalog(edition=config.edition, items=extract_catalog(document))
        if not offline:
            # Only retain a response after chapter extraction succeeds.
            write_bytes(cache / f"{page.id}.html", response.content)

        snapshot = f"en/{page.id}.html"
        snapshots[snapshot] = extracted.content
        chapters.append(
            SourceChapter(
                id=page.id,
                url=response.resolved_url,
                requested_url=page.url,
                title=extracted.title,
                source_byline=extracted.source_byline,
                raw_sha256=sha256(response.content),
                content_sha256=sha256(extracted.content),
                snapshot=snapshot,
                translation=page.translation,
                media=extracted.media,
                excluded_media=extracted.excluded_media,
            )
        )

    # SourceConfig rejects empty page lists at the input boundary.
    assert catalog is not None
    manifest = SourceManifest(
        schema_version=1,
        edition=config.edition,
        canonical_url=config.canonical_url,
        format="Pressbooks HTML adaptation",
        license=config.license,
        current_viva_equivalence=config.current_viva_equivalence,
        retrieved_at=retrieved_at or datetime.now(UTC).isoformat(),
        normalizer_version=1,
        chapters=chapters,
    )
    return PreparedImport(manifest, catalog, snapshots)


def write_import(prepared: PreparedImport, output: Path) -> None:
    """Write individual files atomically, with the manifest last.

    A disk failure can still leave a mixture of old/new files. Import into a
    candidate directory and review before adopting it; no directory transaction
    or automatic modification of Russian translations is provided.
    """
    for relative_path, content in prepared.snapshots.items():
        write_bytes(output / relative_path, content)
    write_json(output / "catalog.json", prepared.catalog)
    write_json(output / "manifest.json", prepared.manifest)


def import_book(
    config: SourceConfig,
    cache: Path,
    output: Path,
    *,
    offline: bool = False,
    retrieved_at: str | None = None,
) -> SourceManifest:
    prepared = prepare_import(config, cache, offline=offline, retrieved_at=retrieved_at)
    write_import(prepared, output)
    return prepared.manifest
