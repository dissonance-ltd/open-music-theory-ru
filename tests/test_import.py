"""Behavioral contracts for source extraction and import orchestration."""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from lxml import html

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from omt.comparison import compare  # noqa: E402
from omt.files import InputError, sha256  # noqa: E402
from omt.importing import PageResponse, import_book  # noqa: E402
from omt.models import SourceConfig, SourcePage  # noqa: E402
from omt.pressbooks import extract_catalog, extract_chapter, parse_chapter  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures"
PAGE = (FIXTURES / "pressbooks.html").read_bytes()


def source_config() -> SourceConfig:
    return SourceConfig(
        edition="fixture",
        canonical_url="https://example.org/",
        source_base="https://example.org/",
        license="CC-BY-SA-4.0",
        current_viva_equivalence="not_verified",
        pages=[SourcePage(id="one", url="https://example.org/c1/", translation="src/one.md")],
    )


class ImportTests(unittest.TestCase):
    def test_v1_normalized_bytes_and_media_are_preserved(self) -> None:
        chapter = parse_chapter(PAGE, "https://example.org/c1/")
        self.assertEqual(chapter.content, (FIXTURES / "normalized.html").read_bytes())
        self.assertIn(b"Definition.", chapter.content)
        self.assertIn(b"https://example.org/fig.png", chapter.content)
        self.assertNotIn(b"unsafe()", chapter.content)
        self.assertNotIn(b"OMT-cover", chapter.content)
        self.assertEqual(chapter.title, "Chapter")
        self.assertEqual(chapter.source_byline, ["An Author"])
        self.assertEqual([item.kind for item in chapter.media], ["img", "iframe"])
        self.assertEqual(len(chapter.excluded_media), 1)

    def test_block_page_is_rejected(self) -> None:
        with self.assertRaisesRegex(InputError, "Missing or ambiguous"):
            parse_chapter(b"<h1>Request blocked</h1>", "https://example.org/")

    def test_unlinked_part_preserves_nested_chapters_and_order(self) -> None:
        raw = b"""<ol class="toc">
          <li id="before"><div class="toc__title__container"><a href="/before/">Before</a></div></li>
          <li id="workbook"><div class="toc__title__container"><span>XII. </span>Workbook</div>
            <ol><li id="digital"><div class="toc__title__container">
              <p><a href="/digital/">Digital Workbook</a></p><p class="toc__author">Kyle Gullings</p>
            </div></li><li id="pdf"><div class="toc__title__container"><a href="/pdf/">PDF Workbook</a></div></li></ol>
          </li><li id="after"><div class="toc__title__container"><a href="/after/">After</a></div></li>
        </ol>"""
        items = extract_catalog(html.fromstring(raw))
        self.assertEqual([item.id for item in items], ["before", "workbook", "after"])
        self.assertEqual(items[1].title, "XII. Workbook")
        self.assertIsNone(items[1].url)
        self.assertEqual([item.id for item in items[1].children], ["digital", "pdf"])
        self.assertEqual(items[1].children[0].url, "/digital/")
        self.assertEqual(items[1].children[0].source_byline, ["Kyle Gullings"])

    def test_repeat_import_preserves_russian_text_and_detects_source_changes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cache = root / "cache"
            cache.mkdir()
            output = root / "upstream"
            translation = root / "src/one.md"
            translation.parent.mkdir()
            translation.write_text("Ручная правка", encoding="utf-8")
            cached = cache / "one.html"
            cached.write_bytes(PAGE)
            first = import_book(
                source_config(), cache, output, offline=True, retrieved_at="2026-09-20"
            )
            second = import_book(
                source_config(), cache, output, offline=True, retrieved_at="2026-09-20"
            )
            self.assertEqual(first, second)
            cached.write_bytes(PAGE.replace(b"A note.", b"A changed note."))
            third = import_book(
                source_config(), cache, output, offline=True, retrieved_at="2026-09-20"
            )
            self.assertEqual(compare(second, third).changed, ["one"])
            self.assertEqual(translation.read_text(encoding="utf-8"), "Ручная правка")

    def test_later_page_failure_does_not_modify_published_import(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cache = root / "cache"
            cache.mkdir()
            (cache / "one.html").write_bytes(PAGE)
            output = root / "upstream"
            config = source_config()
            import_book(config, cache, output, offline=True, retrieved_at="2026-09-20")
            before = {path: path.read_bytes() for path in output.rglob("*") if path.is_file()}
            (cache / "one.html").write_bytes(PAGE.replace(b"A note.", b"Changed."))
            (cache / "two.html").write_bytes(b"<h1>Error</h1>")
            config.pages.append(
                SourcePage(id="two", url="https://example.org/two/", translation=None)
            )
            with self.assertRaises(InputError):
                import_book(config, cache, output, offline=True, retrieved_at="2026-09-20")
            after = {path: path.read_bytes() for path in output.rglob("*") if path.is_file()}
            self.assertEqual(before, after)

    def test_online_import_extracts_once_and_preserves_redirect_url(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            response = PageResponse(PAGE, "https://example.org/redirected/")
            with (
                patch("omt.importing.download_page", return_value=response) as download,
                patch("omt.importing.extract_chapter", wraps=extract_chapter) as extract,
            ):
                manifest = import_book(source_config(), root / "cache", root / "out")
            download.assert_called_once_with("https://example.org/c1/")
            extract.assert_called_once()
            self.assertEqual(manifest.chapters[0].url, response.resolved_url)
            self.assertEqual(manifest.chapters[0].requested_url, "https://example.org/c1/")
            self.assertEqual(manifest.chapters[0].raw_sha256, sha256(PAGE))
            self.assertEqual((root / "cache/one.html").read_bytes(), PAGE)

    def test_offline_import_requires_actual_retrieval_date(self) -> None:
        with self.assertRaisesRegex(InputError, "requires --retrieved-at"):
            import_book(source_config(), Path("unused"), Path("unused"), offline=True)


if __name__ == "__main__":
    unittest.main()
