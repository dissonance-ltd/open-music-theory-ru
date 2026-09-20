"""File schemas. Validation happens once at the JSON/YAML boundary."""

from collections.abc import Iterable
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

PageId = Annotated[str, Field(pattern=r"^[a-z0-9-]+$")]
Sha256 = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
TranslationStatus = Literal["draft", "terminology-reviewed", "content-reviewed", "published"]
TermStatus = Literal["candidate", "accepted", "deprecated"]


def require_unique(values: Iterable[str], label: str) -> None:
    """Reject ambiguous records before callers build dictionaries keyed by ID."""
    seen: set[str] = set()
    for value in values:
        if value in seen:
            raise ValueError(f"Duplicate {label}: {value}")
        seen.add(value)


class Record(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class SourcePage(Record):
    id: PageId
    url: str
    translation: str | None


class SourceConfig(Record):
    edition: str
    canonical_url: str
    source_base: str
    license: str
    current_viva_equivalence: str
    pages: list[SourcePage] = Field(min_length=1)

    @model_validator(mode="after")
    def unique_pages(self) -> Self:
        require_unique((page.id for page in self.pages), "page ID")
        return self


class MediaReference(Record):
    kind: str
    url: str
    alt: str | None
    rights: str = "not_individually_audited"
    distribution: str = "reference_only"


class ExcludedMedia(Record):
    url: str | None
    reason: str


class SourceChapter(Record):
    id: PageId
    url: str
    requested_url: str
    title: str
    source_byline: list[str]
    raw_sha256: Sha256
    content_sha256: Sha256
    snapshot: str
    translation: str | None
    media: list[MediaReference]
    excluded_media: list[ExcludedMedia]


class SourceManifest(Record):
    schema_version: Literal[1]
    edition: str
    canonical_url: str
    format: str
    license: str
    current_viva_equivalence: str
    retrieved_at: str
    normalizer_version: Literal[1]
    chapters: list[SourceChapter]

    @model_validator(mode="after")
    def unique_chapters(self) -> Self:
        require_unique((chapter.id for chapter in self.chapters), "chapter ID")
        require_unique((chapter.snapshot for chapter in self.chapters), "snapshot path")
        return self


class CatalogEntry(Record):
    id: str | None
    title: str
    url: str | None
    source_byline: list[str]
    children: list["CatalogEntry"]


class Catalog(Record):
    edition: str
    items: list[CatalogEntry]


class Translation(Record):
    id: PageId
    path: str
    status: TranslationStatus
    source_content_sha256: Sha256
    reviewed_by: str | None
    modifications: list[str]


class Translations(Record):
    chapters: list[Translation]

    @model_validator(mode="after")
    def unique_translations(self) -> Self:
        require_unique((chapter.id for chapter in self.chapters), "translation ID")
        require_unique((chapter.path for chapter in self.chapters), "translation path")
        return self


class Asset(Record):
    example: int
    source_url: str
    original_reference: str
    path: str
    source_alt: str | None
    license: str
    credit: str
    rights_basis: str
    sha256: Sha256
    retrieved_at: str
    chapter: str | None = None
    translated_caption: str | None = None
    translated_alt: str | None = None


class Assets(Record):
    items: list[Asset]

    @model_validator(mode="after")
    def unique_assets(self) -> Self:
        require_unique((asset.path for asset in self.items), "asset path")
        return self


class Term(Record):
    en: str
    ru: str
    status: TermStatus
    alternatives: list[str] = Field(default_factory=list)
    note: str = ""


class Glossary(Record):
    version: Literal[1]
    status_values: list[TermStatus]
    terms: list[Term]

    @model_validator(mode="after")
    def unique_terms(self) -> Self:
        require_unique((term.en.casefold() for term in self.terms), "English term")
        return self
