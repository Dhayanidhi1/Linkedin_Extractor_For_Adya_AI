import glob
import os
import sys

sys.path.insert(0, r'D:\Project\linkedin_extractor')
os.chdir(r'D:\Project\linkedin_extractor')

from report import generate_report
from config import OUTPUT_DIR

files = glob.glob(os.path.join(OUTPUT_DIR, 'posts_*.json'))
if files:
    latest = max(files, key=os.path.getmtime)
    print(f"Generating report from: {latest}")
    generate_report(latest)
else:
    print("No JSON file found.")
