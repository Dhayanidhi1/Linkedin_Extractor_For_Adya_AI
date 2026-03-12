import sys
from bs4 import BeautifulSoup
import re

with open("output/debug_search.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

author_elements = soup.find_all(class_=re.compile(r'update-components-actor'))
post_wrappers = set()
for a in author_elements:
    p = a.parent
    while p and p.name != 'body':
        if p.name == 'div' and ('search-result' in ' '.join(p.get('class', [])) or 'feed-shared-update' in ' '.join(p.get('class', []))):
            post_wrappers.add(p)
            break
        p = p.parent

with open("output/wrappers.txt", "w", encoding="utf-8") as out:
    out.write(f"Post wrappers found: {len(post_wrappers)}\n")
    for idx, pw in enumerate(list(post_wrappers)[:10]):
        out.write(f"\n--- Wrapper {idx+1} ---\n")
        out.write(f"Classes: {pw.get('class')}\n")
        out.write(f"data-urn: {pw.get('data-urn')}\n")
        out.write(f"data-id: {pw.get('data-id')}\n")
