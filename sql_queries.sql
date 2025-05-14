-- Total number of posts
SELECT COUNT(*) FROM posts

-- Total number of comments on posts
SELECT COUNT(*) FROM comments

-- Total number of comments made on posts by u/sketchdailybot
SELECT COUNT(*)
FROM comments
JOIN posts ON comments.post_id = posts.id
WHERE posts.author = 'sketchdailybot'

-- Counts Average, Min and Max number of comments on posts made by u/sketchdailybot
SELECT AVG(comment_count), MIN(comment_count), MAX(comment_count)
FROM (
    SELECT posts.id, COUNT(comments.id) AS comment_count
    FROM posts
    LEFT JOIN comments ON posts.id = comments.post_id
    WHERE posts.author = 'sketchdailybot'
    GROUP BY posts.id
)

-- Total number of users 
SELECT COUNT(DISTINCT author)
FROM comments
WHERE author IS NOT NULL