import sqlite3
import pandas as pd

# Connect to the SQLite database
conn = sqlite3.connect("sketchdaily.db")

# Step 1: Get post IDs by sketchdailybot
posts_query = """
SELECT id FROM posts WHERE LOWER(author) = 'sketchdailybot';
"""
post_ids = pd.read_sql_query(posts_query, conn)['id'].tolist()

# Step 2: Get all comments on those posts
comments_query = f"""
SELECT id, post_id, parent_id, depth
FROM comments
WHERE post_id IN ({','.join('?' for _ in post_ids)});
"""
comments_df = pd.read_sql_query(comments_query, conn, params=post_ids)

# Step 3: Separate top-level and reply comments
top_level = comments_df[comments_df['parent_id'].str.startswith('t3_')].copy()
replies = comments_df[comments_df['parent_id'].str.startswith('t1_')].copy()

# Step 4: Count replies for each top-level comment
reply_counts = replies['parent_id'].value_counts()
top_level['has_replies'] = top_level['id'].map(lambda cid: f"t1_{cid}" in replies['parent_id'].values)

# Step 5: Calculate max/avg depth of replies per top-level comment
depth_stats = []

for _, row in top_level.iterrows():
    cid = row['id']
    reply_chain = replies[replies['parent_id'] == f"t1_{cid}"]

    # Get all descendant replies recursively
    to_visit = reply_chain['id'].tolist()
    all_depths = reply_chain['depth'].tolist()

    while to_visit:
        children = replies[replies['parent_id'].isin([f"t1_{tid}" for tid in to_visit])]
        all_depths.extend(children['depth'].tolist())
        to_visit = children['id'].tolist()

    if all_depths:
        max_depth = max(all_depths)
        avg_depth = sum(all_depths) / len(all_depths)
        depth_stats.append((cid, max_depth, avg_depth))
    else:
        depth_stats.append((cid, 0, 0.0))

# Summary
num_top_level = len(top_level)
num_no_replies = len(top_level[top_level['has_replies'] == False])
num_with_replies = len(top_level[top_level['has_replies'] == True])

percent_no_replies = (num_no_replies / num_top_level) * 100 if num_top_level else 0
percent_with_replies = (num_with_replies / num_top_level) * 100 if num_top_level else 0

depth_df = pd.DataFrame(depth_stats, columns=['id', 'max_depth', 'avg_depth'])
avg_chain_depth = depth_df[depth_df['max_depth'] > 0]['avg_depth'].mean()
max_chain_depth = depth_df['max_depth'].max()

print(f"Top-level comments on SketchDailyBot posts:")
print(f"  Total: {num_top_level}")
print(f"  No replies: {num_no_replies} ({percent_no_replies:.1f}%)")
print(f"  With replies: {num_with_replies} ({percent_with_replies:.1f}%)")
print(f"  Max depth of reply chains: {max_chain_depth}")
print(f"  Avg depth of reply chains: {avg_chain_depth:.2f}")

conn.close()
