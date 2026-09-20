#!/usr/bin/env python3
"""Validate provenance/assets and, after building, local HTML links and anchors."""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import unquote, urlsplit
from lxml import html
ROOT = Path(__file__).resolve().parents[1]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def check(root=ROOT, built=False):
    manifest = json.loads((root / 'upstream/manifest.json').read_text())
    originals = {c['id']: c for c in manifest['chapters']}
    errors = []
    for c in originals.values():
        p = root / 'upstream' / c['snapshot']
        if not p.is_file() or sha(p) != c['content_sha256']:
            errors.append(f'Source hash mismatch: {p}')
    translations = json.loads((root / 'upstream/translations.json').read_text())['chapters']
    allowed = {'draft', 'terminology-reviewed', 'content-reviewed', 'published'}
    for t in translations:
        p = root / t['path']
        if not p.is_file():
            errors.append(f'Missing translation: {p}')
            continue
        if t['id'] not in originals or t['source_content_sha256'] != originals[t['id']]['content_sha256']:
            errors.append(f'Translation requires source review: {t["id"]}')
        if t['status'] not in allowed:
            errors.append(f'Unknown translation status: {t["status"]}')
        if t['status'] == 'draft' and 'Черновик перевода' not in p.read_text():
            errors.append(f'Missing draft notice: {p}')
        if '{{figure:' in p.read_text():
            errors.append(f'Unresolved figure placeholder: {p}')
    for a in json.loads((root / 'upstream/assets.json').read_text())['items']:
        p = root / a['path']
        if not p.is_file() or sha(p) != a['sha256']:
            errors.append(f'Asset hash mismatch: {p}')
    if built:
        book = root / 'book'
        if not (book / 'index.html').exists():
            errors.append('Run mdbook build first')
        docs = {p: html.parse(str(p)) for p in book.rglob('*.html')}
        for p, doc in docs.items():
            ids = set(doc.xpath('//@id'))
            for element in doc.xpath('//main//a[@href]|//main//img[@src]|//main//iframe[@src]'):
                value = element.get('href') or element.get('src')
                u = urlsplit(value)
                if u.scheme or u.netloc:
                    continue
                target = (p.parent / unquote(u.path)).resolve() if u.path else p.resolve()
                if target.is_dir():
                    target = target / 'index.html'
                if not target.is_file():
                    errors.append(f'Broken local link: {p.name} -> {value}')
                    continue
                if u.fragment and target.suffix == '.html':
                    target_doc = doc if target == p.resolve() else html.parse(str(target))
                    if unquote(u.fragment) not in target_doc.xpath('//@id'):
                        errors.append(f'Missing anchor: {p.name} -> {value}')
            for im in doc.xpath('//main//img'):
                if not im.get('alt', '').strip():
                    errors.append(f'Missing image description: {p.name}')
            for frame in doc.xpath('//main//iframe'):
                if not frame.get('title', '').strip():
                    errors.append(f'Missing iframe title: {p.name}')
    return errors

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--built', action='store_true')
    args = parser.parse_args()
    errors = check(built=args.built)
    if errors:
        raise SystemExit('\n'.join(errors))
    print('Source hashes, translation provenance, assets and requested book checks passed.')
