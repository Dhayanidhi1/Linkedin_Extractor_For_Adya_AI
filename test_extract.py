from bs4 import BeautifulSoup
from parser import parse_post_html
import json

with open("output/debug_search.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

posts = soup.find_all('div', attrs={'data-urn': True})
keywords = ["Shayak Mazumder", "Adya AI"]

extracted = []
for p in posts:
    html_content = str(p)
    data = parse_post_html(html_content, keywords)
    extracted.append(data)

with open("output/test_extracted.json", "w") as f:
    json.dump(extracted, f, indent=2)

print(f"Extracted {len(extracted)} posts. Check output/test_extracted.json.")
