import time
import os
import random
import logging
import sys
from playwright.sync_api import sync_playwright
import re
from config import LINKEDIN_EMAIL, LINKEDIN_PASSWORD, USE_PROXY, PROXY_SERVER, PROXY_USERNAME, PROXY_PASSWORD, OUTPUT_DIR
from parser import parse_post_html

log_file = os.path.join(OUTPUT_DIR, f"scraper_{int(time.time())}.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

STATE_FILE = os.path.join(OUTPUT_DIR, "linkedin_state.json")

def random_sleep(min_sec=2.0, max_sec=5.0):
    time.sleep(random.uniform(min_sec, max_sec))

class LinkedInScraper:
    def __init__(self, keywords, months_back):
        self.keywords = keywords
        self.months_back = months_back
        self.posts_data = []

    def run(self):
        with sync_playwright() as p:
            proxy = None
            if USE_PROXY and PROXY_SERVER:
                proxy = {
                    "server": PROXY_SERVER,
                    "username": PROXY_USERNAME,
                    "password": PROXY_PASSWORD
                }

            # Launch browser
            browser = p.chromium.launch(headless=True, proxy=proxy)
            
            context_args = {
                "viewport": {"width": 1920, "height": 1080},
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            }
            if os.path.exists(STATE_FILE):
                logging.info("Found saved session state.")
                context_args["storage_state"] = STATE_FILE
                
            context = browser.new_context(**context_args)
            page = context.new_page()

            try:
                self._login(page, context)
            except Exception as e:
                logging.error(f"Login failed: {e}")
                browser.close()
                return []

            for keyword in self.keywords:
                logging.info(f"Starting search for: {keyword}")
                try:
                    self._search_keyword(page, keyword)
                except Exception as e:
                    logging.error(f"Error during search for '{keyword}': {e}")
                random_sleep(5, 10)

            browser.close()
            logging.info("Scraping completed.")
            return self.posts_data

    def _login(self, page, context):
        logging.info("Checking login status...")
        page.goto("https://www.linkedin.com/feed/", timeout=60000)
        
        url = page.url.lower()
        if ("feed" in url or "dashboard" in url) and "authwall" not in url and "login" not in url:
            logging.info("Already logged in.")
            return

        logging.info("Not logged in. Performing login...")
        page.goto("https://www.linkedin.com/login", timeout=60000)
        
        try:
            page.fill("input#username, input#session_key", LINKEDIN_EMAIL, timeout=10000)
            random_sleep(1, 2)
            page.fill("input#password, input#session_password", LINKEDIN_PASSWORD, timeout=10000)
            random_sleep(1, 2)
            page.click("button[type='submit']")
            page.wait_for_load_state("networkidle")
        except Exception as e:
            logging.warning(f"Auto-login failed or not a standard login page: {e}. Please log in manually.")
        
        if "checkpoint/challenge" in page.url or "captcha" in page.content().lower() or "login" in page.url:
            logging.warning("CAPTCHA, challenge, or manual login detected! Please solve it manually in the browser. Waiting up to 2 minutes...")
            try:
                page.wait_for_url(lambda url: "feed" in url or "dashboard" in url, timeout=120000)
            except Exception as e:
                logging.error("Did not reach feed after 2 minutes. Exiting.")
                raise Exception("Manual CAPTCHA solving required and timed out.")

        context.storage_state(path=STATE_FILE)
        logging.info("Login successful. State saved.")

    def _search_keyword(self, page, keyword):
        encoded_kw = keyword.replace(" ", "%20")
        search_url = f'https://www.linkedin.com/search/results/content/?keywords=%22{encoded_kw}%22&origin=FACETED_SEARCH&sortBy=%22date_posted%22'
        
        page.goto(search_url)
        page.wait_for_load_state("domcontentloaded")
        random_sleep(2, 4)
        
        SCROLLS = 30 # Approx number of scrolls needed to go 6 months deep
        seen_urns = set()
        
        for i in range(SCROLLS):
            logging.info(f"Scrolling page {i+1}/{SCROLLS} for '{keyword}'...")
            
            for _ in range(3):
                page.keyboard.press("PageDown")
                time.sleep(1)
            
            random_sleep(3, 5)
            
            post_elements = page.locator("div[data-urn]").all()
            
            for index, el in enumerate(post_elements):
                try:
                    urn = el.get_attribute("data-urn")
                    if not urn or urn in seen_urns:
                        continue
                        
                    post_data = {
                        'post_url': f"https://www.linkedin.com/feed/update/{urn}/",
                        'author_name': '',
                        'author_profile_url': '',
                        'post_text': '',
                        'date_posted': '',
                        'likes': 0,
                        'comments': 0,
                        'reposts': 0,
                        'matched_keywords': [],
                        'post_type': 'original'
                    }

                    # Extract Content within this specific post element
                    try:
                        html_content = el.evaluate("node => node.outerHTML")
                        post_data = parse_post_html(html_content, self.keywords)
                        
                        # Add missing bits
                        if not post_data['post_url'] and urn:
                            post_data['post_url'] = f"https://www.linkedin.com/feed/update/{urn}/"
                            
                        # If author_name is empty, we might have an issue, but we still append
                    except Exception as e:
                        logging.warning(f"Failed to parse a post element: {e}")
                        continue

                    seen_urns.add(urn)
                    self.posts_data.append(post_data)
                    logging.info(f"Extracted post {urn} by {post_data.get('author_name', 'Unknown')}")
                    
                except Exception as e:
                    logging.warning(f"Failed to parse a post element: {e}")
                    
            try:
                show_more = page.locator("button:has-text('Show more')")
                if show_more.is_visible():
                    show_more.click()
                    logging.info("Clicked 'Show more' button.")
                    random_sleep(2, 4)
            except Exception:
                pass
                
            if page.locator("text='No more results'").is_visible() or page.locator("text='No results found'").is_visible():
                logging.info("Reached end of search results.")
                break
