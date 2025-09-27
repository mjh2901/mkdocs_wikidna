#!/usr/bin/env python3
"""
Fix spaced emphasis markers in Markdown files.

Converts patterns like:
  - `** text **` -> `**text**`
  - `* text *` -> `*text*`
  - `*** text ***` -> `***text***`

The script skips fenced code blocks (``` / ~~~) and inline code (text enclosed in backticks).

Usage: python3 scripts/fix_bold_spaces.py
"""
import re
from pathlib import Path
from typing import Tuple

ROOT = Path('.')

# Prepare regexes. Order matters: handle triple-asterisk first, then bold, then italic.
TRIPLE_PAT = re.compile(r"\*\*\*\s+(.+?)\s+\*\*\*")
BOLD_PAT = re.compile(r"\*\*\s+(.+?)\s+\*\*")
ITALIC_PAT = re.compile(r"(?<!\*)\*\s+(.+?)\s+\*(?!\*)")

def fix_line_outside_code(text: str) -> Tuple[str, bool]:
    """Fix emphasis spacing in a text piece outside inline code. Returns (new_text, changed)."""
    changed = False
    new = text
    # Apply repeatedly until stable for each pattern
    for pat in (TRIPLE_PAT, BOLD_PAT, ITALIC_PAT):
        while True:
            new2 = pat.sub(lambda m: pat_repl(m), new)
            if new2 == new:
                break
            new = new2
            changed = True
    return new, changed

def pat_repl(m):
    inner = m.group(1)
    # strip only surrounding spaces (already matched) but keep inner spacing
    return m.group(0).replace(m.group(1), inner.strip())


def main():
    md_files = list(ROOT.glob('**/*.md'))
    md_files = [p for p in md_files if '.git/' not in str(p) and 'site/' not in str(p) and 'scripts/.venv' not in str(p)]

    modified = []
    for p in md_files:
        s = p.read_text(encoding='utf-8')
        lines = s.splitlines(True)
        out_lines = []
        in_fence = False
        changed_file = False
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
                    new_part, changed = fix_line_outside_code(parts[i])
                    if changed:
                        parts[i] = new_part
                        changed_file = True
                else:
                    # inside inline code - leave as-is
                    pass
            out_lines.append('`'.join(parts))
        new_s = ''.join(out_lines)
        if changed_file:
            p.write_text(new_s, encoding='utf-8')
            modified.append(str(p))

    print(f"Files modified: {len(modified)}")
    for m in modified:
        print(" -", m)


if __name__ == '__main__':
    main()
