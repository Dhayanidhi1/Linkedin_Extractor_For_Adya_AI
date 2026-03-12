import os
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state="output/linkedin_state.json")
        page = context.new_page()
        print("Navigating to search page...")
        page.goto("https://www.linkedin.com/search/results/content/?keywords=%22Shayak%20Mazumder%22&origin=FACETED_SEARCH&sortBy=%22date_posted%22")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(5000)
        
        with open("output/debug_search.html", "w", encoding="utf-8") as f:
            f.write(page.content())
        print("Done writing to output/debug_search.html")
        browser.close()

if __name__ == "__main__":
    run()
