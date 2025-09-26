#!/usr/bin/env python3
"""
Strict markdown checker that skips fenced code blocks.
Finds:
- MD041: first non-blank line must be H1
- MD010: hard tabs
- MD047: trailing newline issues
- MD022: blank lines around headings (skipping code fences)
- MD058: blank lines around table blocks
- MD007: unordered list indent multiples of 2

Usage: python3 scripts/check_md_strict.py
"""
import re
from pathlib import Path

repo = Path('.').resolve()
docs = repo / 'docs'

heading_re = re.compile(r'^(#{1,6})\s+')
list_re = re.compile(r'^(\s+)[\*-]\s+')

errors = []
for p in sorted(docs.rglob('*.md')):
    rel = p.relative_to(repo)
    text = p.read_text(encoding='utf-8')
    # normalize
    text = text.replace('\r\n','\n').replace('\r','\n')
    lines = text.split('\n')

    # Skip leading blank lines to find first non-blank (not in code fence)
    first_nonblank = None
    in_code = False
    for i,l in enumerate(lines):
        if l.strip().startswith('```') or l.strip().startswith('~~~'):
            in_code = not in_code
            continue
        if in_code:
            continue
        if l.strip():
            first_nonblank = (i+1,l)
            break
    if first_nonblank:
        if not re.match(r'^#\s+\S', first_nonblank[1]):
            errors.append((str(rel),'MD041','First non-blank line is not H1',first_nonblank[0]))
    else:
        errors.append((str(rel),'MD041','File is empty'))

    # check for hard tabs anywhere
    for i,l in enumerate(lines, start=1):
        if '\t' in l:
            errors.append((str(rel),'MD010','Hard tab at line',i))

    # trailing newline checks
    if not text.endswith('\n'):
        errors.append((str(rel),'MD047','File does not end with a single newline'))
    else:
        if text.endswith('\n\n'):
            errors.append((str(rel),'MD047','File ends with multiple trailing newlines'))

    # check headings and tables while skipping fenced code blocks
    in_code = False
    n = len(lines)
    for i,l in enumerate(lines, start=1):
        stripped = l.strip()
        if stripped.startswith('```') or stripped.startswith('~~~'):
            in_code = not in_code
            continue
        if in_code:
            continue
        # heading
        if heading_re.match(l):
            # check previous non-code line
            prev = lines[i-2] if i-2 >= 0 else ''
            nxt = lines[i] if i < n else ''
            if prev.strip() != '':
                errors.append((str(rel),'MD022','No blank line before heading',i))
            if nxt.strip() != '':
                errors.append((str(rel),'MD022','No blank line after heading',i))
        # table detection: '|' in line and not image link or html
        if '|' in l and not re.match(r'!\[.*\]\(.*\)', stripped) and not stripped.startswith('<'):
            prev = lines[i-2] if i-2 >= 0 else ''
            nxt = lines[i] if i < n else ''
            if prev.strip() != '' and '|' not in prev:
                errors.append((str(rel),'MD058','No blank line before table',i))
            if nxt.strip() != '' and '|' not in nxt:
                errors.append((str(rel),'MD058','No blank line after table',i))
        # unordered list indent
        m = list_re.match(l)
        if m:
            sp = len(m.group(1))
            if sp % 2 != 0:
                errors.append((str(rel),'MD007','Unordered list indent not multiple of 2 spaces',i))

if not errors:
    print('OK')
    raise SystemExit(0)
for e in errors:
    print(f"{e[0]}\t{e[1]}\t{e[2]}:{'' if len(e)<4 else e[3]}")
raise SystemExit(2)
