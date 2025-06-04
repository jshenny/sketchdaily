import sqlite3

# Connect to SQLite database (creates it if it doesn't exist)
conn = sqlite3.connect("sketchdaily.db")
c = conn.cursor()

# Create users table
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    account_created INTEGER
)
""")

# Create posts table (with added created_date)
c.execute("""
CREATE TABLE IF NOT EXISTS posts (
    id TEXT PRIMARY KEY,
    title TEXT,
    description TEXT,
    url TEXT,
    author TEXT,
    score INTEGER,
    flair TEXT,
    created_utc INTEGER,
    created_date TEXT,
    FOREIGN KEY (author) REFERENCES users(username)
)
""")

# Create comments table (with added created_date)
c.execute("""
CREATE TABLE IF NOT EXISTS comments (
    id TEXT PRIMARY KEY,
    post_id TEXT,
    parent_id TEXT,
    author TEXT,
    body TEXT,
    depth INTEGER,
    score INTEGER,
    created_utc INTEGER,
    created_date TEXT,
    FOREIGN KEY (post_id) REFERENCES posts(id),
    FOREIGN KEY (author) REFERENCES users(username)
)
""")

# Create user_subreddit_stats table
c.execute("""
CREATE TABLE IF NOT EXISTS user_subreddit_stats (
    username TEXT,
    subreddit TEXT,
    user_flair TEXT,
    total_posts INTEGER,
    total_comments INTEGER,
    total_upvotes INTEGER,
    total_downvotes INTEGER,
    PRIMARY KEY (username, subreddit),
    FOREIGN KEY (username) REFERENCES users(username)
)
""")

# Save and close connection
conn.commit()
conn.close()

print("✅ SQLite schema with readable dates created successfully as sketchdaily_full.db")
