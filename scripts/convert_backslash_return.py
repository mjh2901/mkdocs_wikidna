#!/usr/bin/env python3
"""
Convert double-backslash return markers (e.g. "\\\\") into real newlines in Markdown files.

Behavior:
- Walk all .md files under the repo (excludes .git, site, scripts/.venv)
- Skip fenced code blocks (``` or ~~~)
- Skip inline code (text inside backticks `...`)
- Replace contiguous sequences of two or more backslashes ("\\\\") with a single newline
  inserted at that position.

Run: python3 scripts/convert_backslash_return.py
"""
import re
from pathlib import Path
from typing import Tuple

ROOT = Path('.')

BACKSLASHS_PAT = re.compile(r"\\{2,}")

def convert_text(text: str) -> Tuple[str, bool]:
    """Convert backslash markers outside inline code. Return (new_text, changed)."""
    changed = False
    parts = text.split('`')
    for i in range(len(parts)):
        if i % 2 == 0:
            new_part = BACKSLASHS_PAT.sub('\n', parts[i])
            if new_part != parts[i]:
                parts[i] = new_part
                changed = True
    return '`'.join(parts), changed


def main():
    md_files = [p for p in ROOT.glob('**/*.md') if '.git/' not in str(p) and 'site/' not in str(p) and 'scripts/.venv' not in str(p)]
    modified = []
    for p in md_files:
        s = p.read_text(encoding='utf-8')
        lines = s.splitlines(True)
        out_lines = []
        in_fence = False
        changed_file = False
        for line in lines:
            stripped = line.lstrip()
            if stripped.startswith('```') or stripped.startswith('~~~'):
                in_fence = not in_fence
                out_lines.append(line)
                continue
            if in_fence:
                out_lines.append(line)
                continue
            new_line, changed = convert_text(line)
            if changed:
                changed_file = True
            # new_line may contain embedded newlines; preserve them as separate lines
            out_lines.extend([ln + '\n' if not ln.endswith('\n') else ln for ln in new_line.splitlines()])

        if changed_file:
            new_s = ''.join(out_lines)
            # Normalize accidental double-newlines to single blank lines where appropriate
            # (keep paragraphs separated by a single blank line)
            new_s = re.sub(r"\n{3,}", "\n\n", new_s)
            p.write_text(new_s, encoding='utf-8')
            modified.append(str(p))

    print(f"Files modified: {len(modified)}")
    for m in modified:
        print(" -", m)


if __name__ == '__main__':
    main()
