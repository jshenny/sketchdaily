import sqlite3
import pandas as pd
import re
import matplotlib.pyplot as plt

# Connect to the database
conn = sqlite3.connect('sketchdaily.db')
df = pd.read_sql_query("SELECT body FROM comments WHERE body IS NOT NULL", conn)
conn.close()

# Regex to match any URL
url_pattern = re.compile(r'https?://\S+', re.IGNORECASE)

# Regex for pure Markdown-style links: [text](url)
markdown_link_pattern = re.compile(r'^\s*\[.*?\]\((https?://\S+)\)\s*$', re.IGNORECASE)

# Counters
only_url = 0
text_and_url = 0

for body in df['body']:
    stripped = body.strip()
    print("\nbody: \n" + stripped)
    
    # Case 1: markdown link only
    if markdown_link_pattern.fullmatch(stripped):
        only_url += 1
        print("only url")
    else:
        match = url_pattern.search(stripped)
        if match:
            if stripped == match.group(0):
                print("only url")
                only_url += 1
            else:
                print("url and text")
                text_and_url += 1
        else: 
            print("no url")

# Print results
print(f"Comments with only a URL: {only_url}")
print(f"Comments with text + URL: {text_and_url}")

# Optional: plot the results
labels = ['Only URL', 'Text + URL']
values = [only_url, text_and_url]

plt.figure(figsize=(6, 4))
plt.bar(labels, values, color=['#69b3a2', '#4374B3'])
plt.title('Comments with URLs')
plt.ylabel('Number of Comments')
plt.tight_layout()
plt.show()
