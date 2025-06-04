from dotenv import load_dotenv
import os
import praw
import sqlite3
import time
import prawcore

load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)


SUBREDDIT_NAME = "SketchDaily"
DB_NAME = "sketchdaily_full.db"

# --- Connect to SQLite ---
conn = sqlite3.connect(DB_NAME)
c = conn.cursor()

# --- Helper: Insert or update user and subreddit stats ---
def update_user(username, flair, subreddit_name, is_comment=False, score=0):
    try:
        redditor = reddit.redditor(username)
        created_utc = int(redditor.created_utc)
    except Exception:
        created_utc = None  # If user is deleted or unavailable

    c.execute("INSERT OR IGNORE INTO users (username, account_created) VALUES (?, ?)", (username, created_utc))

    # Initialize or update subreddit-specific stats
    c.execute("""
        INSERT INTO user_subreddit_stats (username, subreddit, user_flair, total_posts, total_comments, total_upvotes, total_downvotes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(username, subreddit) DO UPDATE SET
            user_flair=excluded.user_flair,
            total_posts=total_posts + ?,
            total_comments=total_comments + ?,
            total_upvotes=total_upvotes + ? 
    """, (
        username, subreddit_name, flair,
        0 if is_comment else 1,
        1 if is_comment else 0,
        score, 0,
        0 if is_comment else 1,
        1 if is_comment else 0,
        score
    ))

# --- Recursive comment insert with depth ---
def insert_comment(comment, post_id, depth=1):
    if isinstance(comment, praw.models.MoreComments):
        return
    c.execute("""
        INSERT OR IGNORE INTO comments (id, post_id, parent_id, author, body, depth, score, created_utc)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        comment.id,
        post_id,
        comment.parent_id,
        comment.author.name if comment.author else "[deleted]",
        comment.body,
        depth,
        comment.score,
        int(comment.created_utc)
    ))

    if comment.author:
        flair = comment.author_flair_text or ""
        update_user(comment.author.name, flair, SUBREDDIT_NAME, is_comment=True, score=comment.score)

    for reply in comment.replies:
        insert_comment(reply, post_id, depth + 1)

# --- Main scrape loop ---
import time
import prawcore  # make sure you import this at the top of your file

def scrape_posts(limit=50, start_timestamp=None, end_timestamp=None):
    subreddit = reddit.subreddit(SUBREDDIT_NAME)
    post_count = 0

    for post in subreddit.new(limit=limit):
        if start_timestamp and int(post.created_utc) < start_timestamp:
            continue
        if end_timestamp and int(post.created_utc) > end_timestamp:
            continue

        print(f"🧵 Scraping post: {post.title}")
        try:
            c.execute("""
                INSERT OR IGNORE INTO posts (id, title, description, url, author, score, flair, created_utc)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                post.id,
                post.title,
                post.selftext,
                post.url,
                post.author.name if post.author else "[deleted]",
                post.score,
                post.link_flair_text or "",
                int(post.created_utc)
            ))

            if post.author:
                flair = post.author_flair_text or ""
                update_user(post.author.name, flair, SUBREDDIT_NAME, is_comment=False, score=post.score)

            # Fetch comments and replace MoreComments safely
            try:
                post.comments.replace_more(limit=None)
            except prawcore.exceptions.TooManyRequests as e:
                print("⚠️ Hit Reddit rate limit while loading comments. Sleeping 60 seconds...")
                time.sleep(60)
                continue

            for top_level_comment in post.comments:
                insert_comment(top_level_comment, post.id)

            conn.commit()
            post_count += 1

        except prawcore.exceptions.TooManyRequests:
            print("⚠️ Rate limited by Reddit. Sleeping 60 seconds before retry...")
            time.sleep(60)
            continue
        except Exception as e:
            print(f"❌ Error processing post {post.id}: {e}")
            continue

        # # Respect rate limits: 1 request/sec = 60 req/min
        # time.sleep(1)
    print(f"✅ Finished scraping {post_count} posts.")

# --- Run scraper ---
if __name__ == "__main__":
    # Example: Scrape posts from April 24 to May 8, 2025
    start = int(time.mktime(time.strptime("2020-01-01", "%Y-%m-%d")))
    end = int(time.mktime(time.strptime("2025-05-08", "%Y-%m-%d")))

    scrape_posts(limit=10000, start_timestamp=start, end_timestamp=end)

    conn.close()
    print("✅ Done scraping and inserting into SQLite.")