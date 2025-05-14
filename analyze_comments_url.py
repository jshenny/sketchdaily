import sqlite3
import pandas as pd
import re
import matplotlib.pyplot as plt

# Connect to the SQLite DB
conn = sqlite3.connect('sketchdaily.db')

# SQL: Get top-level comment bodies on SketchDailyBot posts
query = """
SELECT comments.body
FROM comments
JOIN posts ON comments.post_id = posts.id
WHERE LOWER(posts.author) = 'sketchdailybot'
  AND comments.body IS NOT NULL
  AND comments.parent_id LIKE 't3_%';  -- Top-level comments only
"""

df = pd.read_sql_query(query, conn)
conn.close()

# Regex patterns
url_pattern = re.compile(r'https?://\S+', re.IGNORECASE)
markdown_link_pattern = re.compile(r'^\s*\[.*?\]\((https?://\S+)\)\s*$', re.IGNORECASE)

# Counters
only_url = 0
text_and_url = 0
no_url = 0

for body in df['body']:
    stripped = body.strip()

    if markdown_link_pattern.fullmatch(stripped):
        only_url += 1
    else:
        match = url_pattern.search(stripped)
        if match:
            if stripped == match.group(0):
                only_url += 1
            else:
                text_and_url += 1
        else:
            print(stripped)
            no_url += 1

# Totals
total = only_url + text_and_url + no_url
percent_only_url = (only_url / total) * 100 if total else 0
percent_text_and_url = (text_and_url / total) * 100 if total else 0
percent_no_url = (no_url / total) * 100 if total else 0

# Output summary
print("Top-level comments on SketchDailyBot posts:")
print(f"  Only URL       : {only_url} ({percent_only_url:.1f}%)")
print(f"  Text + URL     : {text_and_url} ({percent_text_and_url:.1f}%)")
print(f"  No URL         : {no_url} ({percent_no_url:.1f}%)")
print(f"  Total analyzed : {total}")

# Plot
labels = ['Only URL', 'Text + URL', 'No URL']
values = [only_url, text_and_url, no_url]

plt.figure(figsize=(7, 5))
bars = plt.bar(labels, values, color=['#69b3a2', '#4374B3', '#AAAAAA'])
plt.title('Top-Level Comments with and without URLs (SketchDailyBot posts)')
plt.ylabel('Number of Comments')

# Add percent labels on bars
for bar, pct in zip(bars, [percent_only_url, percent_text_and_url, percent_no_url]):
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2, height + 1, f"{pct:.1f}%", ha='center', va='bottom')

plt.tight_layout()
plt.show()
