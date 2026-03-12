# LinkedIn Posts Extractor

A robust, production-ready Python tool to scrape, parse, and store LinkedIn posts mentioning specific keywords natively using Playwright.

## 🎯 Features
- Automates login and persists session state (saves cookies) to avoid repeated logins.
- Uses Playwright for reliable Javascript rendering and dynamic scrolling.
- Extracts post content, author details, dates, and engagement stats (likes, comments, reposts).
- Saves data to SQLite for deduplication, as well as CSV and JSON formats.
- Generates a neat HTML report with summary statistics and top authors.
- Configurable via `.env` files (Keywords, Proxy support, Headless scraping).

## ⚠️ Important Note on LinkedIn Scraping
Scraping LinkedIn is against their Terms of Service. Be aware that excessive scraping might lead to an account ban. 
- Do not bypass CAPTCHAs programmatically (the script expects a manual login the first time to clear CAPTCHAs).
- Use a dummy/burner account if possible.
- Adhere to rate limits and do not run this aggressively.

## 🛠️ Prerequisites
- Python 3.10+
- Firefox/Chromium via Playwright

## 🚀 Setup Instructions

1. **Change directory into the project**:
```bash
cd C:\Users\dhaya\.gemini\antigravity\scratch\linkedin_extractor
```

2. **Install the required dependencies**:
```bash
py -m pip install -r requirements.txt
py -m playwright install chromium
```

3. **Configure Environment Variables**:
Copy the example config and fill in your details:
```bash
cp .env.example .env
```
Edit `.env` and provide your `LINKEDIN_EMAIL`, `LINKEDIN_PASSWORD`, and desired `KEYWORDS`.
*Note: Set `USE_PROXY=true` and provide proxy details if you wish to route traffic through a proxy.*

## 💻 Running the Scraper

```bash
py main.py
```

### First Run & Captchas
On the very first run, LinkedIn might present a CAPTCHA. If this happens, the script will exit with an error. To solve it:
1. Temporarily open `scraper.py` and change `headless=True` to `headless=False` on line 42 (`browser = p.chromium.launch(...)`).
2. Run the script again. The browser will open.
3. Solve the CAPTCHA manually. 
4. The script will save the session state to `output/linkedin_state.json`.
5. You can now revert to `headless=True` for subsequent automated runs.

## 📁 Output
The `output/` folder will be created and populate with:
- `linkedin_posts.db` (SQLite Database containing all deduplicated posts logic)
- `posts_{timestamp}.json` (JSON dump of the current run)
- `posts_{timestamp}.csv` (CSV dump of the current run)
- `linkedin_report.html` (A summary dashboard)
- `scraper_{timestamp}.log` (Activity & debug logs)
