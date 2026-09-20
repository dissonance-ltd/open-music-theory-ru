"""Local links and accessibility labels in the generated mdBook HTML."""

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlsplit

from lxml import html

from .pressbooks import elements


@dataclass(frozen=True)
class BookPage:
    path: Path
    document: html.HtmlElement
    anchors: set[str]


def load_page(path: Path) -> BookPage:
    document = html.parse(str(path)).getroot()
    anchors = {node.get("id", "") for node in elements(document, ".//*[@id]")}
    if document.get("id"):
        anchors.add(document.get("id", ""))
    return BookPage(path.resolve(), document, anchors)


def check_page_links(page: BookPage, pages: dict[Path, BookPage]) -> list[str]:
    errors = []
    query = "//main//a[@href]|//main//img[@src]|//main//iframe[@src]"
    for element in elements(page.document, query):
        value = element.get("href") or element.get("src") or ""
        url = urlsplit(value)
        if url.scheme or url.netloc:
            continue
        target = (page.path.parent / unquote(url.path)).resolve() if url.path else page.path
        if target.is_dir():
            target = target / "index.html"
        if not target.is_file():
            errors.append(f"Broken local link: {page.path.name} -> {value}")
            continue
        if url.fragment and target.suffix == ".html":
            target_page = pages.get(target)
            if target_page is None:
                target_page = load_page(target)
                pages[target] = target_page
            if unquote(url.fragment) not in target_page.anchors:
                errors.append(f"Missing anchor: {page.path.name} -> {value}")
    return errors


def check_accessibility_labels(page: BookPage) -> list[str]:
    errors = []
    for image in elements(page.document, "//main//img"):
        if not image.get("alt", "").strip():
            errors.append(f"Missing image description: {page.path.name}")
    for frame in elements(page.document, "//main//iframe"):
        if not frame.get("title", "").strip():
            errors.append(f"Missing iframe title: {page.path.name}")
    return errors


def check_built_book(book: Path) -> list[str]:
    if not (book / "index.html").is_file():
        return ["Run mdbook build first"]
    pages = {path.resolve(): load_page(path) for path in sorted(book.rglob("*.html"))}
    errors = []
    # Link resolution may cache additional target pages; do not mutate an iterator.
    for page in list(pages.values()):
        errors.extend(check_page_links(page, pages))
        errors.extend(check_accessibility_labels(page))
    return errors
