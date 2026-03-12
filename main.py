import os
import glob
from config import KEYWORDS, MONTHS_BACK, OUTPUT_DIR
from scraper import LinkedInScraper
from storage import save_posts
from report import generate_report

def main():
    print("="*50)
    print("🚀 Starting LinkedIn Scraper")
    print(f"Keywords: {KEYWORDS}")
    print(f"Months back: {MONTHS_BACK}")
    print("="*50)
    
    scraper = LinkedInScraper(KEYWORDS, MONTHS_BACK)
    posts_data = scraper.run()
    
    if posts_data:
        print(f"\n[MAIN] Extracted {len(posts_data)} posts. Saving to storage...")
        save_posts(posts_data)
        
        # Find latest json file to generate report
        list_of_files = glob.glob(os.path.join(OUTPUT_DIR, '*.json'))
        if list_of_files:
            latest_file = max(list_of_files, key=os.path.getctime)
            generate_report(latest_file)
    else:
        print("\n[MAIN] No posts were extracted.")

if __name__ == "__main__":
    main()
