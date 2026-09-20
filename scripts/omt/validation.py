"""Independent checks for source provenance, translations and local assets."""

from pathlib import Path

from .files import file_sha256, read_json
from .html_checks import check_built_book
from .models import Assets, SourceManifest, Translations


def check_source_snapshots(root: Path, manifest: SourceManifest) -> list[str]:
    errors = []
    for chapter in manifest.chapters:
        path = root / "upstream" / chapter.snapshot
        if not path.is_file() or file_sha256(path) != chapter.content_sha256:
            errors.append(f"Source hash mismatch: {path}")
    return errors


def check_translations(
    root: Path, manifest: SourceManifest, translations: Translations
) -> list[str]:
    errors = []
    sources = {chapter.id: chapter for chapter in manifest.chapters}
    for translation in translations.chapters:
        path = root / translation.path
        if not path.is_file():
            errors.append(f"Missing translation: {path}")
            continue
        source = sources.get(translation.id)
        if source is None or translation.source_content_sha256 != source.content_sha256:
            errors.append(f"Translation requires source review: {translation.id}")
        text = path.read_text(encoding="utf-8")
        if translation.status == "draft" and "Черновик перевода" not in text:
            errors.append(f"Missing draft notice: {path}")
        if "{{figure:" in text:
            errors.append(f"Unresolved figure placeholder: {path}")
    return errors


def check_assets(root: Path, assets: Assets) -> list[str]:
    errors = []
    for asset in assets.items:
        path = root / asset.path
        if not path.is_file() or file_sha256(path) != asset.sha256:
            errors.append(f"Asset hash mismatch: {path}")
    return errors


def check(root: Path, *, built: bool = False) -> list[str]:
    manifest = read_json(root / "upstream/manifest.json", SourceManifest)
    translations = read_json(root / "upstream/translations.json", Translations)
    assets = read_json(root / "upstream/assets.json", Assets)
    errors = check_source_snapshots(root, manifest)
    errors.extend(check_translations(root, manifest, translations))
    errors.extend(check_assets(root, assets))
    if built:
        errors.extend(check_built_book(root / "book"))
    return errors
