#!/usr/bin/env python3
"""Compare imported chapter hashes without modifying translations."""
import argparse
import json
from pathlib import Path

def compare(old, new):
    a = {c['id']: c for c in old['chapters']}
    b = {c['id']: c for c in new['chapters']}
    return {
        'added': sorted(b.keys() - a.keys()),
        'removed': sorted(a.keys() - b.keys()),
        'changed': sorted(k for k in a.keys() & b.keys() if a[k]['content_sha256'] != b[k]['content_sha256']),
        'metadata_changed': sorted(k for k in a.keys() & b.keys() if any(a[k].get(f) != b[k].get(f) for f in ('url', 'source_byline', 'title'))),
        'edition_changed': old.get('edition') != new.get('edition'),
    }

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('old', type=Path)
    p.add_argument('new', type=Path)
    args = p.parse_args()
    result = compare(json.loads(args.old.read_text()), json.loads(args.new.read_text()))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(int(any(result.values())))
