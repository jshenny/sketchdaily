import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import re

# Connect to the database
conn = sqlite3.connect('sketchdaily.db')

# Query total comments
total_comments = pd.read_sql_query("""
SELECT COUNT(*) FROM comments
WHERE author IS NOT NULL AND author != '[deleted]';
""", conn).iloc[0, 0]

# Query unique users
unique_users = pd.read_sql_query("""
SELECT COUNT(DISTINCT author) FROM comments
WHERE author IS NOT NULL AND author != '[deleted]';
""", conn).iloc[0, 0]

# Query comment counts per user
df_comments = pd.read_sql_query("""
SELECT author, COUNT(*) AS comment_count
FROM comments
WHERE author IS NOT NULL AND author != '[deleted]'
GROUP BY author;
""", conn)

# Query user flair
df_flair = pd.read_sql_query("""
SELECT username, user_flair
FROM user_subreddit_stats
WHERE user_flair IS NOT NULL AND user_flair LIKE '%/%';
""", conn)

conn.close()

# Merge flair into comment counts
df = df_comments.merge(df_flair, left_on='author', right_on='username', how='left')

# Extract days posted (the second number in the flair)
def extract_days(flair):
    try:
        return int(flair.split('/')[1])
    except:
        return None

df['days_posted'] = df['user_flair'].apply(extract_days)

# Calculate stats
avg_comments = total_comments / unique_users if unique_users else 0
avg_days = df['days_posted'].dropna().mean()
max_days = df['days_posted'].dropna().max()

# Print summary
print(f"Total comments                  : {total_comments}")
print(f"Unique users                   : {unique_users}")
print(f"Average comments per user      : {avg_comments:.2f}")
print(f"Average days posted (from flair): {avg_days:.2f}")
print(f"Max days posted (from flair)    : {max_days}")

# Plot histogram of comment counts
plt.figure(figsize=(10, 6))
plt.hist(df['comment_count'], bins=50, color='skyblue', edgecolor='black')
plt.title('Distribution of Comment Counts per User')
plt.xlabel('Number of Comments')
plt.ylabel('Number of Users')
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()
