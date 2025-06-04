import sqlite3
import os
from datetime import datetime

# Connect to database
conn = sqlite3.connect("sketchdaily_full.db")
c = conn.cursor()

# Ensure output directory exists
output_dir = "monthly_chats"
os.makedirs(output_dir, exist_ok=True)

# Get all "Free Chat" posts
c.execute("""
    SELECT id, title, created_utc
    FROM posts
    WHERE title LIKE '%Free Chat%'
""")
monthly_posts = c.fetchall()

for post_id, title, created_utc in monthly_posts:
    # Get all comments for the post
    c.execute("""
        SELECT author, body
        FROM comments
        WHERE post_id = ?
        ORDER BY created_utc ASC
    """, (post_id,))
    comments = c.fetchall()

    # Format filename: YYYY-MM_Free_Chat.txt
    date_str = datetime.utcfro_
