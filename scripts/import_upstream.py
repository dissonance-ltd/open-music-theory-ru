#!/usr/bin/env python3
"""Import explicitly selected Pressbooks HTML pages; never write Russian chapters.

A dated HTML adaptation is used until an official VIVA export is available.
Run with --offline against cached downloads for deterministic extraction.
"""
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urljoin, urlsplit
from urllib.request import urlopen
from lxml import html, etree

ROOT = Path(__file__).resolve().parents[1]

def digest(data):
    return hashlib.sha256(data).hexdigest()

def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def text(node):
    return ' '.join(node.text_content().split())

def extract(raw, url):
    doc = html.fromstring(raw)
    containers = doc.xpath('//*[@id="content"]/section')
    if len(containers) != 1:
        raise ValueError(f'Missing or ambiguous Pressbooks chapter: {url}')
    if not doc.xpath('//a[contains(@href,"creativecommons.org/licenses/by-sa/4.0")]'):
        raise ValueError(f'Expected page CC BY-SA 4.0 notice: {url}')
    section = copy.deepcopy(containers[0])
    titles = section.xpath('./header//h1')
    if not titles:
        raise ValueError(f'Missing title: {url}')
    title = text(titles[0])
    byline = [text(e) for e in section.xpath('./header//*[@data-type="author"]')]
    # This is the byline of the adaptation, not necessarily original authorship.
    metadata = {'title': title, 'source_byline': byline}
    excluded = []
    for img in section.xpath('.//img'):
        if re.search(r'OMT-cover|OMT-logo', img.get('src', ''), re.I):
            excluded.append({'url': img.get('src'), 'reason': 'Reserved cover/logo artwork by Bethany Nistler'})
            img.drop_tree()
    # Preserve hidden glossary definitions as readable English source text.
    for template in section.xpath('.//template'):
        template.tag = 'div'
    for node in section.xpath('.//script|.//style|.//button|./header'):
        node.drop_tree()
    for comment in section.xpath('.//comment()'):
        comment.getparent().remove(comment)
    for node in section.iter():
        if not isinstance(node.tag, str):
            continue
        for attr in list(node.attrib):
            if attr.lower().startswith('on') or attr in {'style', 'srcdoc', 'srcset', 'sizes', 'fetchpriority', 'decoding', 'tabindex'}:
                del node.attrib[attr]
        for attr in ('href', 'src'):
            value = node.get(attr)
            if value and not value.startswith('#'):
                resolved = urljoin(url, value)
                if urlsplit(resolved).scheme not in {'http', 'https', 'mailto'}:
                    del node.attrib[attr]
                else:
                    node.set(attr, resolved)
    section.tag = 'article'
    section.attrib.clear()
    encoded = (html.tostring(section, encoding='unicode', pretty_print=True) + '\n').encode('utf-8')
    media = []
    for element in section.xpath('.//img|.//iframe|.//audio|.//video|.//source|.//a[@href]'):
        target = element.get('src') or element.get('href') or ''
        if element.tag == 'a' and not re.search(r'\.(pdf|docx|mscz|mp3|wav)(?:[?#]|$)', target, re.I):
            continue
        media.append({'kind': element.tag, 'url': target, 'alt': element.get('alt'),
                      'rights': 'not_individually_audited', 'distribution': 'reference_only'})
    return encoded, metadata, media, excluded

def catalog(raw):
    doc = html.fromstring(raw)
    tocs = doc.xpath('//ol[@class="toc"]')
    if len(tocs) != 1:
        raise ValueError('Expected one Pressbooks table of contents')
    def entries(ol):
        result = []
        for li in ol.xpath('./li'):
            headings = li.xpath('./div[contains(@class,"toc__title__container")]')
            if not headings:
                raise ValueError('Missing Pressbooks TOC heading')
            anchors = headings[0].xpath('.//a[@href]')
            a = anchors[0] if anchors else None
            authors = li.xpath('./div/p[contains(@class,"toc__author")]')
            # Unlinked part headings still contain chapters (e.g. Workbook).
            item = {'id': li.get('id'), 'title': text(a if a is not None else headings[0]),
                    'url': a.get('href') if a is not None else None,
                    'source_byline': [text(e) for e in authors], 'children': []}
            for child in li.xpath('./ol'):
                item['children'].extend(entries(child))
            result.append(item)
        return result
    return entries(tocs[0])

def import_book(config, cache, output, offline=False, retrieved_at=None):
    # Parse everything before writing, so a failed fetch/parse cannot update the manifest.
    records, prepared, toc = [], {}, None
    for page in config['pages']:
        slug = page['id']
        if not re.fullmatch(r'[a-z0-9-]+', slug):
            raise ValueError(f'Unsafe page id: {slug}')
        cached = cache / (slug + '.html')
        if offline:
            raw = cached.read_bytes()
            resolved = page['url']
        else:
            with urlopen(page['url'], timeout=45) as response:
                raw = response.read()
                resolved = response.url
            # Validate before retaining a response as a usable cache file.
            extract(raw, resolved)
            cache.mkdir(parents=True, exist_ok=True)
            cached.write_bytes(raw)
        content, metadata, media, excluded = extract(raw, resolved)
        if toc is None:
            toc = catalog(raw)
        path = f'en/{slug}.html'
        prepared[path] = content
        records.append({'id': slug, 'url': resolved, 'requested_url': page['url'],
                        **metadata, 'raw_sha256': digest(raw), 'content_sha256': digest(content),
                        'snapshot': path, 'translation': page.get('translation'),
                        'media': media, 'excluded_media': excluded})
    stamp = retrieved_at or datetime.now(timezone.utc).isoformat()
    manifest = {'schema_version': 1, 'edition': config['edition'],
                'canonical_url': config['canonical_url'], 'format': 'Pressbooks HTML adaptation',
                'license': config['license'], 'current_viva_equivalence': config['current_viva_equivalence'],
                'retrieved_at': stamp, 'normalizer_version': 1, 'chapters': records}
    for path, content in prepared.items():
        destination = output / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
    write_json(output / 'manifest.json', manifest)
    write_json(output / 'catalog.json', {'edition': config['edition'], 'items': toc})
    return manifest

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=ROOT / 'upstream/sources.json')
    parser.add_argument('--cache', type=Path, default=ROOT / '.cache/omt')
    parser.add_argument('--output', type=Path, default=ROOT / 'upstream')
    parser.add_argument('--offline', action='store_true')
    parser.add_argument('--retrieved-at', help='Actual retrieval timestamp for offline cache imports')
    args = parser.parse_args()
    if args.offline and not args.retrieved_at:
        parser.error('--offline requires --retrieved-at (do not relabel an old cache as freshly fetched)')
    result = import_book(json.loads(args.config.read_text()), args.cache, args.output, args.offline, args.retrieved_at)
    print(f'Imported {len(result["chapters"])} English snapshots. Russian chapters were not modified.')
