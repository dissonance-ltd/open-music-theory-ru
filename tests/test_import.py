import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from import_upstream import extract, import_book
from diff_upstream import compare

PAGE = b'''<html><nav><ol class="toc"><li id="c1"><div class="toc__title__container"><a href="https://example.org/c1/">One</a></div></li></ol></nav><div id="content"><section><header><h1>Chapter</h1><p data-type="author">An Author</p></header><p id="claim">A note.</p><img src="../fig.png" alt="Notes"><img src="OMT-cover.png"><iframe src="https://www.youtube.com/embed/example" title="Example"></iframe><script>unsafe()</script><template id="term"><p>Definition.</p><button>Close</button></template></section></div><a href="https://creativecommons.org/licenses/by-sa/4.0/">License</a></html>'''

class ImportTests(unittest.TestCase):
    def test_text_media_definitions_and_rights_survive_normalization(self):
        content, meta, media, excluded = extract(PAGE, 'https://example.org/c1/')
        self.assertIn(b'A note.', content)
        self.assertIn(b'Definition.', content)
        self.assertIn(b'https://example.org/fig.png', content)
        self.assertIn(b'iframe', content)
        self.assertNotIn(b'unsafe()', content)
        self.assertNotIn(b'OMT-cover', content)
        self.assertEqual(meta['source_byline'], ['An Author'])
        self.assertEqual(len(media), 2)
        self.assertEqual(len(excluded), 1)

    def test_block_page_is_rejected(self):
        with self.assertRaises(ValueError):
            extract(b'<h1>Request blocked</h1>', 'https://example.org/')

    def test_repeat_import_preserves_russian_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); cache = root / 'cache'; cache.mkdir()
            output = root / 'upstream'; ru = root / 'src/one.md'; ru.parent.mkdir(); ru.write_text('Ручная правка')
            (cache / 'one.html').write_bytes(PAGE)
            config = {'edition':'fixture','canonical_url':'https://example.org/','license':'CC-BY-SA-4.0','current_viva_equivalence':'not_verified','pages':[{'id':'one','url':'https://example.org/c1/','translation':'src/one.md'}]}
            one = import_book(config, cache, output, True, '2026-09-20')
            two = import_book(config, cache, output, True, '2026-09-20')
            self.assertEqual(one, two)
            self.assertEqual(ru.read_text(), 'Ручная правка')
            (cache / 'one.html').write_bytes(PAGE.replace(b'A note.', b'A changed note.'))
            three = import_book(config, cache, output, True, '2026-09-20')
            self.assertEqual(compare(two, three)['changed'], ['one'])
            self.assertEqual(ru.read_text(), 'Ручная правка')
            before = (output / 'manifest.json').read_bytes()
            (cache / 'one.html').write_bytes(b'<h1>Error</h1>')
            with self.assertRaises(ValueError):
                import_book(config, cache, output, True, '2026-09-20')
            self.assertEqual((output / 'manifest.json').read_bytes(), before)

    def test_removed_chapters_and_edition_changes_are_reported(self):
        old = {'edition':'old', 'chapters':[{'id':'a','content_sha256':'1'}]}
        new = {'edition':'new', 'chapters':[]}
        self.assertEqual(compare(old, new)['removed'], ['a'])
        self.assertTrue(compare(old, new)['edition_changed'])

if __name__ == '__main__':
    unittest.main()
