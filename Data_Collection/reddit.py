import praw
import csv
import os
import dotenv

dotenv.load_dotenv()
client_id = os.getenv("REDDIT_CLIENT_ID")
client_secret = os.getenv("REDDIT_SECRET")

reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    user_agent="Reddit MOT133A group2",
)

def fetch_comments_for_posts(query, limit=25, filename="reddit_comments.csv"):
    posts = reddit.subreddit("all").search(query, sort="relevance", limit=limit)

    if not os.path.exists("reddit"):
        os.makedirs("reddit")

    with open(filename, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([
            "id",
            "Post ID",
            "Post Title",
            "Comment ID",
            "Author",
            "Comment Body",
            "Score",
            "Created UTC"  # Unix timestamp (seconds since epoch)
        ])

        comment_id_counter = 1  # incremental ID for each comment

        for post in posts:
            print(f"Fetching comments for post: {post.id} - {post.title}")
            post.comments.replace_more(limit=None)
            all_comments = post.comments.list()

            for comment in all_comments:
                writer.writerow([
                    comment_id_counter,
                    post.id,
                    post.title,
                    comment.id,
                    str(comment.author),
                    comment.body.replace('\n', ' ').replace('\r', ' '),
                    comment.score,
                    comment.created_utc
                ])
                comment_id_counter += 1

            print(f"Saved {len(all_comments)} comments for post {post.id}")

    print(f"\nDone! Comments saved to {filename}")

def main():
    search_term = "bic cristal"
    # search_term = "sailor pro gear"
    max_posts = 1000

    filename = f"reddit/reddit_comments_{search_term.replace(' ', '_')}_{max_posts}.csv"
    fetch_comments_for_posts(
        query=search_term,
        limit=max_posts,
        filename=filename
    )

if __name__ == "__main__":
    main()
