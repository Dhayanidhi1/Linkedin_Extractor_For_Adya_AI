import re
from bs4 import BeautifulSoup

with open("output/debug_search.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

urn_elements = soup.find_all(attrs={'data-urn': True})
print(f"Elements with data-urn: {len(urn_elements)}")

urna_list = [el['data-urn'] for el in urn_elements]
for idx, urn in enumerate(urna_list[:20]):
    print(f"{idx+1}. {urn}")

print("\nLet's also look for standard search result elements without data-urn")
# Usually search results in LinkedIn have 'search-results-container' or 'search-result__occluded-item' class
search_items = soup.find_all('div', class_=re.compile(r'search-result__'))
print(f"search_result__ elements: {len(search_items)}")
for si in list(search_items)[:3]:
    print(si.get('class'))

# Let's search by typical Feed Post wrapper in search results
# e.g., 'feed-shared-update-v2'
feed_items = soup.find_all('div', class_=re.compile(r'feed-shared-update-v2'))
print(f"feed-shared-update-v2 elements: {len(feed_items)}")
for fi in list(feed_items)[:3]:
    print(f"Classes: {fi.get('class')}")
    print(f"data-urn: {fi.get('data-urn')}")
