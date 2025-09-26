#!/usr/bin/env python3
"""
Rename `start.md` files to `index.md` across docs/, and update links.
- For each docs/**/start.md -> docs/**/index.md (skip if index.md exists and record conflict)
- Update all markdown files to rewrite links and href/src attributes:
  - replace 'start.md' -> 'index.md'
  - replace '/.../start/' -> '/.../'
  - replace '.../start/' -> '.../'
  - if a URL becomes empty (was exactly 'start/' or 'start'), replace with './'

This script is conservative: it logs conflicts and only renames where safe.
"""
import re
import os
from pathlib import Path

root = Path('.').resolve()
docs = root / 'docs'
if not docs.exists():
    print('Error: docs/ not found here')
    raise SystemExit(2)

start_files = list(docs.rglob('start.md'))
print(f'Found {len(start_files)} start.md files')
conflicts = []
renamed = []
for s in start_files:
    tgt = s.with_name('index.md')
    if tgt.exists():
        conflicts.append((str(s), str(tgt)))
        print(f'SKIP rename: target exists {tgt} (source {s})')
        continue
    s.rename(tgt)
    renamed.append((str(s), str(tgt)))
    print(f'Renamed {s} -> {tgt}')

# Update links in all markdown files
md_files = list(docs.rglob('*.md'))
link_md = re.compile(r'(!?\[.*?\])\(([^)]+)\)')
# html attributes like href="..." or src='...'
html_attr = re.compile(r"(href|src)=(\"|'')([^\"'>]+)(\"|'')")

changes = []
for p in md_files:
    text = p.read_text(encoding='utf-8')
    orig = text
    # function to transform a URL
    def transform_url(url):
        new = url
        # ignore external schemes
        if re.match(r'^(?:[a-zA-Z]+:)?//', new) or re.match(r'^[a-zA-Z0-9+.-]+:', new):
            return new
        # replace start.md -> index.md
        new = new.replace('start.md', 'index.md')
        # remove '/start/' segments
        new = re.sub(r'(/)start(/)', r'\1', new)
        # remove trailing 'start/' at end
        if new.endswith('start/'):
            new = new[:-6]
        # remove '/start' before fragments or end
        new = re.sub(r'/start(?=#|$)', '/', new)
        # remove 'start' at start
        if new == 'start' or new == 'start/':
            new = './'
        # if new is empty, make it './'
        if new == '':
            new = './'
        return new
    # replace markdown link urls
    def repl_md(m):
        text_label = m.group(1)
        url = m.group(2)
        new_url = transform_url(url)
        if new_url != url:
            return f"{text_label}({new_url})"
        return m.group(0)
    text = link_md.sub(repl_md, text)
    # replace html attrs
    def repl_html(m):
        attr = m.group(1)
        q = m.group(2)
        url = m.group(3)
        q2 = m.group(4)
        new_url = transform_url(url)
        if new_url != url:
            return f"{attr}={q}{new_url}{q2}"
        return m.group(0)
    text = html_attr.sub(repl_html, text)
    if text != orig:
        p.write_text(text, encoding='utf-8')
        changes.append(str(p))
        print(f'Updated links in {p}')

print('\nSummary:')
print(f'Renamed: {len(renamed)}')
for a,b in renamed[:200]:
    print(f'- {a} -> {b}')
print(f'Conflicts (skipped): {len(conflicts)}')
for a,b in conflicts[:200]:
    print(f'- {a} (target exists {b})')
print(f'Markdown files updated: {len(changes)}')
for f in changes[:200]:
    print(f'- {f}')

if conflicts:
    print('\nNote: Some folders already had index.md; those start.md files were not renamed. Review conflicts manually.')
