#!/usr/bin/env python3
"""
Lightweight internal link and anchor checker for MkDocs-generated site/
- Scans all HTML files under site/
- Collects all element ids (anchors) per file
- Checks all internal <a href="..."> links: that target file exists, and fragment anchors exist
- Skips external links (http(s)://, //), mailto:, tel:, javascript:

Usage: run after `mkdocs build` so site/ is present.
"""
import os
import sys
from html.parser import HTMLParser
from urllib.parse import urlparse, urldefrag, unquote

ROOT = os.path.join(os.getcwd(), 'site')
if not os.path.isdir(ROOT):
    print('site/ directory not found; run `mkdocs build` first', file=sys.stderr)
    sys.exit(2)

class IdHrefParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.hrefs = []  # list of (href, lineno)
    def handle_starttag(self, tag, attrs):
        ad = dict(attrs)
        if 'id' in ad:
            self.ids.add(ad['id'])
        if tag == 'a' and 'href' in ad:
            self.hrefs.append(ad['href'])

# gather ids and hrefs per file
file_ids = {}
file_hrefs = {}
html_files = []
for dirpath,dirnames,filenames in os.walk(ROOT):
    for fn in filenames:
        if fn.lower().endswith('.html'):
            path = os.path.join(dirpath, fn)
            html_files.append(path)
            data = open(path,'rb').read()
            try:
                text = data.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    text = data.decode('latin-1')
                except Exception:
                    text = ''
            p = IdHrefParser()
            try:
                p.feed(text)
            except Exception:
                pass
            rel = os.path.relpath(path, ROOT)
            file_ids[rel] = p.ids
            file_hrefs[rel] = p.hrefs

# helper to resolve a link href relative to an html file
def resolve_target(source_rel, href):
    href = unquote(href.split('#',1)[0])
    if href.strip() == '':
        return source_rel, ''
    # if href is fragment-only
    if href.startswith('#'):
        return source_rel, href[1:]
    # skip absolute urls
    parsed = urlparse(href)
    if parsed.scheme in ('http','https','mailto','tel','javascript') or href.startswith('//'):
        return None, None
    # make path relative to source; handle root-relative paths starting with '/'
    src_dir = os.path.dirname(source_rel)
    path = parsed.path
    if path.startswith('/'):
        # root-relative: drop leading slash
        candidate = os.path.normpath(path.lstrip('/'))
    else:
        candidate = os.path.normpath(os.path.join(src_dir, path))
    # If candidate is directory, append index.html
    # Normalize slashes for consistent keys
    candidate = candidate.replace('\\', '/')

    full_candidate = os.path.join(ROOT, candidate)
    # If candidate is a directory, use its index.html
    if os.path.isdir(full_candidate):
        candidate = os.path.join(candidate, 'index.html')
        full_candidate = os.path.join(ROOT, candidate)

    # If no extension, try candidate + '.html'
    if not os.path.splitext(candidate)[1]:
        if os.path.exists(full_candidate + '.html'):
            candidate = candidate + '.html'
            full_candidate = os.path.join(ROOT, candidate)

    # If candidate doesn't exist, try candidate + '/index.html'
    if not os.path.exists(full_candidate):
        if os.path.exists(os.path.join(ROOT, candidate, 'index.html')):
            candidate = os.path.join(candidate, 'index.html')
            full_candidate = os.path.join(ROOT, candidate)

    return candidate.replace('\\','/'), (href.split('#',1)[1] if '#' in href else '')

broken = []
checked = 0
for src, hrefs in file_hrefs.items():
    for h in hrefs:
        checked += 1
        tgt, frag = resolve_target(src, h)
        if tgt is None and frag is None:
            # external link; skip
            continue
        if tgt is None:
            continue
        tgt_path = os.path.join(ROOT, tgt) if tgt else os.path.join(ROOT, src)
        tgt_rel = tgt if tgt else src
        if not os.path.exists(tgt_path):
            broken.append((src, h, 'target-not-found', tgt_rel))
            continue
        if frag:
            ids = file_ids.get(tgt_rel.replace('\\','/'), set())
            if frag not in ids:
                broken.append((src, h, 'anchor-not-found', tgt_rel + '#' + frag))

# report
print(f'Scanned {len(html_files)} HTML files, checked {checked} links.')
if not broken:
    print('No broken internal links or anchors found.')
    sys.exit(0)
print('\nBroken links and anchors:')
for b in broken:
    print(f'- In {b[0]} -> "{b[1]}" => {b[2]} ({b[3]})')
sys.exit(1)
