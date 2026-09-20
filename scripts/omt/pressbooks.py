"""Pressbooks-specific extraction. No network or filesystem operations here.

This preserves normalizer v1 output. The resulting archival HTML is not a
security-sanitized document and must stay outside the published book source.
"""

import copy
import re
from dataclasses import dataclass
from typing import cast
from urllib.parse import urljoin, urlsplit

from lxml import html

from .files import InputError
from .models import CatalogEntry, ExcludedMedia, MediaReference

LICENSE_XPATH = '//a[contains(@href,"creativecommons.org/licenses/by-sa/4.0")]'
RESERVED_ARTWORK = re.compile(r"OMT-cover|OMT-logo", re.IGNORECASE)
ATTACHMENT = re.compile(r"\.(pdf|docx|mscz|mp3|wav)(?:[?#]|$)", re.IGNORECASE)
REMOVED_ATTRIBUTES = {"style", "srcdoc", "srcset", "sizes", "fetchpriority", "decoding", "tabindex"}
ALLOWED_SCHEMES = {"http", "https", "mailto"}


@dataclass(frozen=True)
class ExtractedChapter:
    content: bytes
    title: str
    source_byline: list[str]
    media: list[MediaReference]
    excluded_media: list[ExcludedMedia]


def elements(node: html.HtmlElement, xpath: str) -> list[html.HtmlElement]:
    """Typed boundary for XPath expressions that select HTML elements only."""
    return cast(list[html.HtmlElement], node.xpath(xpath))


def element_text(node: html.HtmlElement) -> str:
    return " ".join(node.text_content().split())


def remove_reserved_artwork(section: html.HtmlElement) -> list[ExcludedMedia]:
    excluded = []
    for image in elements(section, ".//img"):
        if RESERVED_ARTWORK.search(image.get("src", "")):
            excluded.append(
                ExcludedMedia(
                    url=image.get("src"),
                    reason="Reserved cover/logo artwork by Bethany Nistler",
                )
            )
            image.drop_tree()
    return excluded


def normalize_markup(section: html.HtmlElement, source_url: str) -> None:
    """Apply v1 cleanup in place, keeping its operation order and serialization."""
    for template in elements(section, ".//template"):
        template.tag = "div"
    for node in elements(section, ".//script|.//style|.//button|./header"):
        node.drop_tree()
    for comment in section.xpath(".//comment()"):
        comment.getparent().remove(comment)
    for node in section.iter():
        if not isinstance(node.tag, str):
            continue
        for attribute in list(node.attrib):
            if attribute.lower().startswith("on") or attribute in REMOVED_ATTRIBUTES:
                del node.attrib[attribute]
        for attribute in ("href", "src"):
            value = node.get(attribute)
            if not value or value.startswith("#"):
                continue
            resolved = urljoin(source_url, value)
            if urlsplit(resolved).scheme in ALLOWED_SCHEMES:
                node.set(attribute, resolved)
            else:
                del node.attrib[attribute]
    section.tag = "article"
    section.attrib.clear()


def collect_media(section: html.HtmlElement) -> list[MediaReference]:
    references = []
    query = ".//img|.//iframe|.//audio|.//video|.//source|.//a[@href]"
    for element in elements(section, query):
        target = element.get("src") or element.get("href") or ""
        if element.tag == "a" and not ATTACHMENT.search(target):
            continue
        references.append(
            MediaReference(
                kind=str(element.tag),
                url=target,
                alt=element.get("alt"),
                rights="not_individually_audited",
                distribution="reference_only",
            )
        )
    return references


def extract_chapter(document: html.HtmlElement, source_url: str) -> ExtractedChapter:
    sections = elements(document, '//*[@id="content"]/section')
    if len(sections) != 1:
        raise InputError(f"Missing or ambiguous Pressbooks chapter: {source_url}")
    if not elements(document, LICENSE_XPATH):
        raise InputError(f"Expected page CC BY-SA 4.0 notice: {source_url}")
    section = copy.deepcopy(sections[0])
    titles = elements(section, "./header//h1")
    if not titles:
        raise InputError(f"Missing title: {source_url}")
    title = element_text(titles[0])
    byline = [element_text(node) for node in elements(section, './header//*[@data-type="author"]')]
    excluded = remove_reserved_artwork(section)
    normalize_markup(section, source_url)
    content = (html.tostring(section, encoding="unicode", pretty_print=True) + "\n").encode("utf-8")
    return ExtractedChapter(content, title, byline, collect_media(section), excluded)


def parse_chapter(raw: bytes, source_url: str) -> ExtractedChapter:
    return extract_chapter(html.fromstring(raw), source_url)


def catalog_entries(ordered_list: html.HtmlElement) -> list[CatalogEntry]:
    entries = []
    for item in elements(ordered_list, "./li"):
        headings = elements(item, './div[contains(@class,"toc__title__container")]')
        if not headings:
            raise InputError("Missing Pressbooks TOC heading")
        anchors = elements(headings[0], ".//a[@href]")
        anchor = anchors[0] if anchors else None
        authors = elements(item, './div/p[contains(@class,"toc__author")]')
        children = []
        for child_list in elements(item, "./ol"):
            children.extend(catalog_entries(child_list))
        entries.append(
            CatalogEntry(
                id=item.get("id"),
                title=element_text(anchor if anchor is not None else headings[0]),
                url=anchor.get("href") if anchor is not None else None,
                source_byline=[element_text(author) for author in authors],
                children=children,
            )
        )
    return entries


def extract_catalog(document: html.HtmlElement) -> list[CatalogEntry]:
    tables = elements(document, '//ol[@class="toc"]')
    if len(tables) != 1:
        raise InputError("Expected one Pressbooks table of contents")
    return catalog_entries(tables[0])
