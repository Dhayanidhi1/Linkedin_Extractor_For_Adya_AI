from bs4 import BeautifulSoup
import re

with open("output/debug_search.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

# In search results, posts might be wrapped differently than in the regular feed.
# Let's look for known post-like elements by checking for author names or 'update-components-actor'
author_elements = soup.find_all(class_=re.compile(r'update-components-actor'))
print(f"Author elements found: {len(author_elements)}")

# Let's find their large parent containers
post_wrappers = set()
for a in author_elements:
    # Go up the tree until we find a parent that looks like a main container
    p = a.parent
    while p and p.name != 'body':
        if p.name == 'div' and (p.has_attr('data-urn') or p.has_attr('data-id') or 'search-result' in ' '.join(p.get('class', [])) or 'feed-shared-update' in ' '.join(p.get('class', []))):
            post_wrappers.add(p)
            break
        p = p.parent

print(f"Post wrappers found: {len(post_wrappers)}")
for idx, pw in enumerate(list(post_wrappers)[:5]):
    print(f"\n--- Wrapper {idx+1} ---")
    print(f"Classes: {pw.get('class')}")
    print(f"data-urn: {pw.get('data-urn')}")
    print(f"data-id: {pw.get('data-id')}")
    # Print a tiny snippet
    print(str(pw)[:200])
