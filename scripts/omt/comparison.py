"""Compare source manifests without reading or changing translation files."""

from .models import Record, SourceChapter, SourceManifest


class ManifestDiff(Record):
    added: list[str]
    removed: list[str]
    changed: list[str]
    metadata_changed: list[str]
    edition_changed: bool

    @property
    def has_changes(self) -> bool:
        return bool(
            self.added
            or self.removed
            or self.changed
            or self.metadata_changed
            or self.edition_changed
        )


def metadata_changed(previous: SourceChapter, current: SourceChapter) -> bool:
    return (
        previous.url != current.url
        or previous.source_byline != current.source_byline
        or previous.title != current.title
    )


def compare(previous: SourceManifest, current: SourceManifest) -> ManifestDiff:
    previous_chapters = {chapter.id: chapter for chapter in previous.chapters}
    current_chapters = {chapter.id: chapter for chapter in current.chapters}
    previous_ids = previous_chapters.keys()
    current_ids = current_chapters.keys()
    changed = []
    changed_metadata = []
    for chapter_id in sorted(previous_ids & current_ids):
        old_chapter = previous_chapters[chapter_id]
        new_chapter = current_chapters[chapter_id]
        if old_chapter.content_sha256 != new_chapter.content_sha256:
            changed.append(chapter_id)
        if metadata_changed(old_chapter, new_chapter):
            changed_metadata.append(chapter_id)
    return ManifestDiff(
        added=sorted(current_ids - previous_ids),
        removed=sorted(previous_ids - current_ids),
        changed=changed,
        metadata_changed=changed_metadata,
        edition_changed=previous.edition != current.edition,
    )
