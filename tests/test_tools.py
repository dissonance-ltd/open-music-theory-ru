"""Schema errors, comparison, pure rendering, book checks and CLI contracts."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pydantic import BaseModel, ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from omt.comparison import compare  # noqa: E402
from omt.files import (  # noqa: E402
    InputError,
    read_json,
    read_yaml,
    sha256,
    write_bytes,
    write_json,
)
from omt.glossary import render  # noqa: E402
from omt.html_checks import check_built_book  # noqa: E402
from omt.models import (  # noqa: E402
    Asset,
    Assets,
    Glossary,
    SourceChapter,
    SourceConfig,
    SourceManifest,
    Term,
    Translation,
    Translations,
)
from omt.validation import check_assets, check_source_snapshots, check_translations  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def manifest() -> SourceManifest:
    return SourceManifest(
        schema_version=1,
        edition="fixture",
        canonical_url="https://example.org/",
        format="Pressbooks HTML adaptation",
        license="CC-BY-SA-4.0",
        current_viva_equivalence="not_verified",
        retrieved_at="2026-09-20",
        normalizer_version=1,
        chapters=[
            SourceChapter(
                id="one",
                url="https://example.org/one/",
                requested_url="https://example.org/one/",
                title="One",
                source_byline=["An Author"],
                raw_sha256=sha256(b"raw"),
                content_sha256=sha256(b"source"),
                snapshot="en/one.html",
                translation="src/one.md",
                media=[],
                excluded_media=[],
            )
        ],
    )


class SchemaTests(unittest.TestCase):
    def test_duplicate_ids_fail_before_comparison(self) -> None:
        data = manifest().model_dump()
        data["chapters"].append(data["chapters"][0])
        with self.assertRaisesRegex(ValidationError, "Duplicate chapter ID: one"):
            SourceManifest.model_validate(data)

    def test_malformed_field_error_includes_file_and_location(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            data = manifest().model_dump()
            data["chapters"][0]["content_sha256"] = "invalid"
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(InputError) as raised:
                read_json(path, SourceManifest)
            self.assertIn(str(path), str(raised.exception))
            self.assertIn("chapters.0.content_sha256", str(raised.exception))

    def test_wrong_types_unknown_fields_and_empty_config_are_rejected(self) -> None:
        data = manifest().model_dump()
        changes: list[dict[str, object]] = [{"normalizer_version": "1"}, {"unknown": True}]
        for change in changes:
            with self.subTest(change=change), self.assertRaises(ValidationError):
                SourceManifest.model_validate(data | change)
        config = json.loads((ROOT / "upstream/sources.json").read_text(encoding="utf-8"))
        config["pages"] = []
        with self.assertRaises(ValidationError):
            SourceConfig.model_validate(config)

    def test_duplicate_translation_asset_and_glossary_keys_are_rejected(self) -> None:
        cases: list[tuple[str, type[BaseModel], str]] = [
            ("upstream/translations.json", Translations, "chapters"),
            ("upstream/assets.json", Assets, "items"),
            ("glossary/terminology.yml", Glossary, "terms"),
        ]
        for path, schema, collection in cases:
            with self.subTest(path=path):
                model = (
                    read_yaml(ROOT / path, schema)
                    if path.endswith(".yml")
                    else read_json(ROOT / path, schema)
                )
                data = model.model_dump()
                data[collection].append(data[collection][0])
                with self.assertRaisesRegex(ValidationError, "Duplicate"):
                    schema.model_validate(data)


class ComparisonTests(unittest.TestCase):
    def test_content_metadata_additions_removals_and_edition(self) -> None:
        previous = manifest()
        current = previous.model_copy(deep=True)
        current.chapters[0].title = "New title"
        current.chapters[0].content_sha256 = sha256(b"updated source")
        current.chapters.append(
            current.chapters[0].model_copy(update={"id": "two", "snapshot": "en/two.html"})
        )
        current.edition = "new edition"
        difference = compare(previous, current)
        self.assertEqual(difference.changed, ["one"])
        self.assertEqual(difference.metadata_changed, ["one"])
        self.assertEqual(difference.added, ["two"])
        self.assertTrue(difference.edition_changed)
        current.chapters = []
        self.assertEqual(compare(previous, current).removed, ["one"])
        self.assertFalse(compare(previous, previous).has_changes)


class GlossaryTests(unittest.TestCase):
    def test_render_escapes_cells_and_preserves_sort_order_and_alternatives(self) -> None:
        glossary = Glossary(
            version=1,
            status_values=["candidate"],
            terms=[
                Term(en="z", ru="я", status="candidate"),
                Term(en="A|B", ru="а\nб", status="candidate", note="note", alternatives=["other"]),
            ],
        )
        rendered = render(glossary)
        self.assertIn(r"A\|B | а б | note Варианты: other. | кандидат", rendered)
        self.assertLess(rendered.index(r"A\|B"), rendered.index("| z |"))

    def test_committed_glossary_is_byte_compatible(self) -> None:
        glossary = read_yaml(ROOT / "glossary/terminology.yml", Glossary)
        self.assertEqual(render(glossary).encode("utf-8"), (ROOT / "src/glossary.md").read_bytes())


class ValidationTests(unittest.TestCase):
    def test_hashes_stale_bindings_draft_notices_and_placeholders(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "upstream/en").mkdir(parents=True)
            (root / "upstream/en/one.html").write_bytes(b"source")
            sources = manifest()
            self.assertEqual(check_source_snapshots(root, sources), [])
            (root / "upstream/en/one.html").write_bytes(b"changed")
            self.assertIn("Source hash mismatch", check_source_snapshots(root, sources)[0])
            translations = Translations(
                chapters=[
                    Translation(
                        id="one",
                        path="src/one.md",
                        status="draft",
                        source_content_sha256=sha256(b"stale"),
                        reviewed_by=None,
                        modifications=[],
                    )
                ]
            )
            self.assertIn("Missing translation", check_translations(root, sources, translations)[0])
            (root / "src").mkdir()
            (root / "src/one.md").write_text("{{figure:1}}", encoding="utf-8")
            errors = check_translations(root, sources, translations)
            self.assertEqual(len(errors), 3)
            self.assertTrue(any("requires source review" in error for error in errors))
            self.assertTrue(any("Missing draft notice" in error for error in errors))
            self.assertTrue(any("placeholder" in error for error in errors))
            assets = Assets(
                items=[
                    Asset(
                        example=1,
                        source_url="https://example.org/a.png",
                        original_reference="a.png",
                        path="src/a.png",
                        source_alt=None,
                        license="CC-BY-SA-4.0",
                        credit="Author",
                        rights_basis="fixture",
                        sha256=sha256(b"image"),
                        retrieved_at="2026-09-20",
                    )
                ]
            )
            self.assertIn("Asset hash mismatch", check_assets(root, assets)[0])
            (root / "src/a.png").write_bytes(b"image")
            self.assertEqual(check_assets(root, assets), [])

    def test_built_links_encoded_anchors_and_accessibility_labels(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            book = Path(directory)
            (book / "index.html").write_text(
                """<html><body><main>
                <a id="here" href="#here">same page</a>
                <a href="chapter.html#%D0%B4%D0%BE">encoded anchor</a>
                <a href="https://example.org/unavailable">external is not checked</a>
                <a href="missing.html">broken file</a>
                <a href="chapter.html#missing">broken anchor</a>
                <img src="image.png" alt=" "><iframe src="https://example.org/video"></iframe>
                </main></body></html>""",
                encoding="utf-8",
            )
            (book / "chapter.html").write_text(
                '<html><head><meta charset="utf-8"></head><body><main><h1 id="до">До</h1></main></body></html>',
                encoding="utf-8",
            )
            (book / "image.png").write_bytes(b"fixture")
            errors = check_built_book(book)
            self.assertEqual(len(errors), 4)
            for expected in [
                "Broken local link",
                "Missing anchor",
                "Missing image description",
                "Missing iframe title",
            ]:
                self.assertTrue(any(expected in error for error in errors))
            self.assertFalse(any("encoded" in error or "%D0" in error for error in errors))

    def test_missing_build_reports_actionable_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(check_built_book(Path(directory)), ["Run mdbook build first"])

    def test_failed_file_replacement_preserves_original_and_cleans_temporary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "output.json"
            path.write_bytes(b"old")
            with patch.object(Path, "replace", side_effect=OSError("disk error")):
                with self.assertRaisesRegex(OSError, "disk error"):
                    write_bytes(path, b"new")
            self.assertEqual(path.read_bytes(), b"old")
            self.assertEqual(list(path.parent.iterdir()), [path])


class CliTests(unittest.TestCase):
    def test_diff_exit_codes_and_input_error_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            previous_path, current_path = root / "old.json", root / "new.json"
            previous = manifest()
            write_json(previous_path, previous)
            write_json(current_path, previous)
            command = [
                sys.executable,
                str(ROOT / "scripts/diff_upstream.py"),
                str(previous_path),
                str(current_path),
            ]
            equal = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertEqual(equal.returncode, 0, equal.stderr)
            current = previous.model_copy(update={"edition": "another"})
            write_json(current_path, current)
            changed = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertEqual(changed.returncode, 1, changed.stderr)
            self.assertTrue(json.loads(changed.stdout)["edition_changed"])
            current_path.write_text('{"chapters": "bad"}', encoding="utf-8")
            invalid = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertEqual(invalid.returncode, 2)
            self.assertIn(str(current_path), invalid.stderr)
            self.assertNotIn("Traceback", invalid.stderr)

    def test_all_entry_points_work_outside_repository(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            for script in ["import_upstream", "diff_upstream", "render_glossary", "check_book"]:
                with self.subTest(script=script):
                    result = subprocess.run(
                        [sys.executable, str(ROOT / f"scripts/{script}.py"), "--help"],
                        cwd=directory,
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn("usage:", result.stdout)


if __name__ == "__main__":
    unittest.main()
