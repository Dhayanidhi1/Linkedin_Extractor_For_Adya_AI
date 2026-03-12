import json
from bs4 import BeautifulSoup
import re

with open("output/debug_search.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

posts = soup.find_all('div', attrs={'data-urn': re.compile('.*activity.*')})

def summarize_element(el):
    if not hasattr(el, 'name'):
        return None
    classes = el.get('class', [])
    data = {
        'tag': el.name,
        'class': classes,
        'text': el.get_text(separator=' ', strip=True)[:100] if el.get_text(strip=True) else '',
    }
    for k, v in el.attrs.items():
        if k not in ['class']:
            data[k] = v
    if len(el.find_all(recursive=False)) > 0:
        data['children'] = [summarize_element(c) for c in el.find_all(recursive=False)]
        data['children'] = [c for c in data['children'] if c is not None]
    return data

result = []
for p in posts[:2]:
    result.append(summarize_element(p))

with open("output/DOM_summary.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2)

print(f"Dumped {len(result)} posts to output/DOM_summary.json")
