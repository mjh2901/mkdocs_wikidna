#!/usr/bin/env python3
"""
Fix bold spacing in Markdown files.
Replaces occurrences of "** text **" with "**text**" outside code fences and inline code.

Usage: python3 scripts/fix_bold_spaces.py
"""
import re
from pathlib import Path

ROOT = Path('.')
patterns = ["** text **"]

md_files = list(ROOT.glob('**/*.md'))
# exclude .git and site dirs
md_files = [p for p in md_files if '.git/' not in str(p) and 'site/' not in str(p) and 'scripts/.venv' not in str(p)]

bold_pat = re.compile(r"\*\*\s+([^*]+?)\s+\*\*")

modified = []
for p in md_files:
    s = p.read_text(encoding='utf-8')
    lines = s.splitlines(True)
    out_lines = []
    in_fence = False
    changed = False
    for line in lines:
        stripped = line.lstrip()
        # detect fenced code blocks starting with ``` or ~~~
        if stripped.startswith('```') or stripped.startswith('~~~'):
            in_fence = not in_fence
            out_lines.append(line)
            continue
        if in_fence:
            out_lines.append(line)
            continue
        # handle inline code by splitting on backticks and only transforming outside inline code
        parts = line.split('`')
        for i in range(0, len(parts)):
            if i % 2 == 0:
                # outside inline code - repeatedly replace until stable
                new = parts[i]
                while True:
                    new2 = bold_pat.sub(r"**\1**", new)
                    if new2 == new:
                        break
                    new = new2
                if new != parts[i]:
                    parts[i] = new
                    changed = True
            else:
                # inside inline code - leave as-is
                pass
        out_lines.append('`'.join(parts))
    new_s = ''.join(out_lines)
    if changed:
        p.write_text(new_s, encoding='utf-8')
        modified.append(str(p))

print(f"Files modified: {len(modified)}")
for m in modified:
    print(" -", m)
