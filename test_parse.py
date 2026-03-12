from bs4 import BeautifulSoup
import re
import json

with open("output/debug_search.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

print("Total elements:", len(soup.find_all()))

# Look for posts using common linkedin data attributes
posts_by_urn = soup.find_all(lambda tag: tag.has_attr('data-urn') and 'activity' in tag['data-urn'])
print(f"Elements with data-urn containing 'activity': {len(posts_by_urn)}")

# Often they might be in search result wrappers
search_results = soup.find_all('div', class_=re.compile(r'search-results-container|search-result__occluded-item|feed-shared-update-v2', re.I))
print(f"Elements with typical post classes: {len(search_results)}")

# Let's see if we can extract data-urn from the first few
if posts_by_urn:
    post = posts_by_urn[0]
    print(f"\nFirst Post URN: {post['data-urn']}")
    print(f"First Post HTML snippet (first 500 chars):")
    print(str(post)[:500])
else:
    print("No posts found by data-urn. Let's look for standard feed wrappers.")
    feed_items = soup.find_all('div', attrs={'data-id': True})
    print(f"Elements with data-id: {len(feed_items)}")
    
    # Check for authors to locate posts
    authors = soup.find_all('span', class_=re.compile(r'update-components-actor__name|entity-result__title-text', re.I))
    print(f"Elements matching author names: {len(authors)}")
    if authors:
        print("\nFirst Author HTML snippet:")
        print(str(authors[0].parent))
