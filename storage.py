import sqlite3
import pandas as pd
import json
import os
from datetime import datetime
from config import OUTPUT_DIR

DB_PATH = os.path.join(OUTPUT_DIR, "linkedin_posts.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            post_url TEXT PRIMARY KEY,
            author_name TEXT,
            author_profile_url TEXT,
            post_text TEXT,
            date_posted TEXT,
            likes INTEGER,
            comments INTEGER,
            reposts INTEGER,
            matched_keywords TEXT,
            post_type TEXT,
            scraped_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_posts(posts_data):
    if not posts_data:
        print("[STORAGE] No posts data to save.")
        return
    
    init_db()
    
    # Save to SQLite (with deduplication)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    new_posts_added = 0
    for post in posts_data:
        try:
            cursor.execute('''
                INSERT INTO posts (
                    post_url, author_name, author_profile_url, post_text, 
                    date_posted, likes, comments, reposts, matched_keywords, 
                    post_type, scraped_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                post.get('post_url'), post.get('author_name'), post.get('author_profile_url'),
                post.get('post_text'), post.get('date_posted'), post.get('likes'),
                post.get('comments'), post.get('reposts'), json.dumps(post.get('matched_keywords', [])),
                post.get('post_type'), datetime.now().isoformat()
            ))
            new_posts_added += 1
        except sqlite3.IntegrityError:
            # Post URL already exists, deduplicate by ignoring
            pass
            
    conn.commit()
    conn.close()
    
    # Save to CSV & JSON
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    df = pd.DataFrame(posts_data)
    csv_path = os.path.join(OUTPUT_DIR, f"posts_{timestamp}.csv")
    json_path = os.path.join(OUTPUT_DIR, f"posts_{timestamp}.json")
    
    df.to_csv(csv_path, index=False, encoding='utf-8')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(posts_data, f, indent=4, ensure_ascii=False)
        
    print(f"[STORAGE] Stored {new_posts_added} new posts to SQLite DB")
    print(f"[STORAGE] Batch saved to {csv_path}")
    print(f"[STORAGE] Batch saved to {json_path}")
