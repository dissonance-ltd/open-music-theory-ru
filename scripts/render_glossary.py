#!/usr/bin/env python3
from pathlib import Path
import argparse
import yaml
ROOT = Path(__file__).resolve().parents[1]

def render():
    data = yaml.safe_load((ROOT / 'glossary/terminology.yml').read_text())
    lines = ['# Рабочий глоссарий', '', 'Все соответствия со статусом «кандидат» требуют рецензирования. Эта страница генерируется из `glossary/terminology.yml`.', '', '| English | Русский термин | Примечание | Статус |', '|---|---|---|---|']
    for term in sorted(data['terms'], key=lambda t: t['en'].lower()):
        note = term.get('note', '')
        if term.get('alternatives'):
            note += ' Варианты: ' + ', '.join(term['alternatives']) + '.'
        values = [term['en'], term['ru'], note, {'candidate': 'кандидат', 'accepted': 'принято', 'deprecated': 'не используется'}[term['status']]]
        lines.append('| ' + ' | '.join(v.replace('|', '\\|').replace('\n', ' ') for v in values) + ' |')
    return '\n'.join(lines) + '\n'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    path = ROOT / 'src/glossary.md'
    expected = render()
    if args.check:
        if path.read_text() != expected:
            raise SystemExit('Regenerate glossary: python scripts/render_glossary.py')
    else:
        path.write_text(expected)
