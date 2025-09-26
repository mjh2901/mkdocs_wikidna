#!/usr/bin/env python3
"""
Fix common Markdown mechanical style issues across docs/:
- Ensure single trailing newline (MD047)
- Promote first non-blank heading to H1 if present (MD041)
- Ensure blank line before/after headings (MD022)
- Ensure blank line before/after table blocks (MD058)

This script is conservative: it only promotes an existing heading to H1
and never invents headings for files that start with content.
"""
import re
from pathlib import Path

docs = Path('docs')
md_files = sorted(docs.rglob('*.md'))
changed_files = []

heading_re = re.compile(r'^(#{1,6})\s+(.*)$')
code_fence_re = re.compile(r'^(```|~~~)')

for p in md_files:
    text = p.read_text(encoding='utf-8')
    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    lines = text.split('\n')
    orig_lines = list(lines)
    changed = False

    # Remove trailing blank lines at EOF
    while len(lines) > 0 and lines[-1].strip() == '':
        lines.pop()
        changed = True
    # Ensure single trailing newline later when writing

    # Find first non-blank line
    first_idx = None
    for i,l in enumerate(lines):
        if l.strip() != '':
            first_idx = i
            break

    if first_idx is not None:
        m = heading_re.match(lines[first_idx])
        if m:
            # If it's a heading but not H1, promote to H1
            if m.group(1) != '#':
                lines[first_idx] = '# ' + m.group(2).strip()
                changed = True

    # Ensure blank lines around headings and tables, avoid modifying inside code fences
    out = []
    in_code = False
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if code_fence_re.match(line.strip()):
            # toggle code fence
            in_code = not in_code
            out.append(line)
            i += 1
            continue
        if not in_code:
            # Heading handling: ensure blank line before and after
            if heading_re.match(line):
                # before
                if len(out) > 0 and out[-1].strip() != '':
                    out.append('')
                    changed = True
                out.append(line)
                # after: lookahead to next non-empty line
                # If next line exists and is non-empty and not a heading, insert blank
                if i+1 < n and lines[i+1].strip() != '':
                    # If next is a heading, we still prefer a blank line between headings
                    out.append('')
                    changed = True
                i += 1
                continue
            # Table handling: detect blocks with '|' that are not in a list or code
            if '|' in line:
                # crude table detection: at least one '|' and not image/link-only
                # find contiguous block
                # ensure previous line is blank
                # We'll collect the block
                j = i
                block = []
                while j < n and '|' in lines[j]:
                    block.append(lines[j])
                    j += 1
                # before block
                if len(out) > 0 and out[-1].strip() != '':
                    out.append('')
                    changed = True
                out.extend(block)
                # after block
                if j < n and lines[j].strip() != '':
                    out.append('')
                    changed = True
                i = j
                continue
        # default
        out.append(line)
        i += 1

    # Ensure file ends with a single newline
    final = '\n'.join(out).rstrip('\n') + '\n'

    if final != text:
        p.write_text(final, encoding='utf-8')
        changed_files.append(str(p))

print('Fixed files:', len(changed_files))
for f in changed_files[:200]:
    print(f)

if len(changed_files) == 0:
    print('No files needed changes.')

