#!/usr/bin/env python3
"""Convert .txt files in the docs/ tree (DokuWiki-like markup) to Markdown .md files.

Rules applied (conservative):
- DokuWiki headings (== ... ==) -> Markdown # headings (level = number of =, capped at 6)
- Links of form [[url|text]] -> [text](url)
- Links of form [[url]] -> [url](url)
- Other [[internal links]] -> plain text (internal links not rewritten)
- Emphasis: //// -> ** (bold), //text// -> *text* (italic)
- Convert simple horizontal rules of ---- to ---

The script writes .md files next to the .txt files and leaves the .txt files unchanged.
"""

import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'

def convert_content(text: str) -> str:
    # Headings: lines like "===== Title ====="
    def heading_repl(m):
        equals = m.group(1)
        title = m.group(2).strip()
        level = min(len(equals), 6)
        return f"{('#' * level)} {title}"

    text = re.sub(r'^(=+)\s*(.*?)\s*\1\s*$', heading_repl, text, flags=re.MULTILINE)

    # Links: [[http...|Text]] -> [Text](http...)
    text = re.sub(r"\[\[(https?://[^\|\]]+)\|([^\]]+)\]\]", r"[\2](\1)", text)
    # Links: [[http...]] -> [http...](http...)
    text = re.sub(r"\[\[(https?://[^\]]+)\]\]", r"[\1](\1)", text)
    # Other internal/wiki links [[Page|Label]] or [[Page]] -> Label or Page (no link)
    text = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", r"\2", text)
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)

    # Bold/italics: replace //// with ** first, then //...// -> *...*
    text = text.replace('////', '**')
    text = re.sub(r'//([^/].*?)//', r'*\1*', text, flags=re.DOTALL)

    # Horizontal rule
    text = re.sub(r'^----+$', '---', text, flags=re.MULTILINE)

    # Trim trailing spaces on lines
    text = '\n'.join([line.rstrip() for line in text.splitlines()]) + '\n'

    return text


def main():
    converted = 0
    errors = []
    for dirpath, dirnames, filenames in os.walk(DOCS):
        for fn in filenames:
            if not fn.lower().endswith('.txt'):
                continue
            src = Path(dirpath) / fn
            dst = src.with_suffix('.md')
            try:
                text = src.read_text(encoding='utf-8')
                new = convert_content(text)
                dst.write_text(new, encoding='utf-8')
                converted += 1
            except Exception as e:
                errors.append((str(src), str(e)))

    print(f'Converted {converted} .txt files to .md')
    if errors:
        print('\nErrors:')
        for p, e in errors:
            print(p, e)


if __name__ == '__main__':
    if not DOCS.exists():
        print(f'Docs directory not found at {DOCS}')
        raise SystemExit(1)
    main()
