from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd
import os
import dotenv

# Load environment variables from .env file
dotenv.load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")  # Replace with your key

youtube = build("youtube", "v3", developerKey=API_KEY)

def search_youtube(query, max_results=100):
    videos = []
    next_page_token = None

    while len(videos) < max_results:
        response = youtube.search().list(
            q=query,
            part="id,snippet",
            type="video",
            maxResults=min(50, max_results - len(videos)),
            pageToken=next_page_token
        ).execute()

        for item in response.get("items", []):
            video_id = item["id"].get("videoId")
            snippet = item.get("snippet", {})
            if video_id:
                videos.append({
                    "video_id": video_id,
                    "title": snippet.get("title"),
                    "channel": snippet.get("channelTitle"),
                    "published_at": snippet.get("publishedAt")
                })

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return pd.DataFrame(videos)

def get_comments(video_id, max_comments=200):
    comments = []
    next_page_token = None

    while True:
        try:
            response = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=100,
                pageToken=next_page_token,
                textFormat="plainText"
            ).execute()
        except HttpError as e:
            print(f"Skipping video {video_id} due to error: {e}")
            return pd.DataFrame()

        for item in response.get("items", []):
            comment = item["snippet"]["topLevelComment"]["snippet"]
            comments.append({
                "video_id": video_id,
                "author": comment["authorDisplayName"],
                "text": comment["textDisplay"],
                "published_at": comment["publishedAt"],
                "like_count": comment["likeCount"]
            })

        next_page_token = response.get("nextPageToken")
        if not next_page_token or len(comments) >= max_comments:
            break

    return pd.DataFrame(comments)

# --- Main flow ---

def main():
    search_term = "sailor pro gear"
    # search_term = "bic cristal"
    max_videos = 1000
    max_comments_per_video = 10000
    
    # Search videos
    videos_df = search_youtube(search_term, max_results=max_videos)
    print("Found videos:")
    print(videos_df)

    # Fetch comments for each video and combine
    all_comments = pd.DataFrame()

    for vid in videos_df['video_id']:
        print(f"Fetching comments for video: {vid}")
        comments_df = get_comments(vid, max_comments=max_comments_per_video)
        all_comments = pd.concat([all_comments, comments_df], ignore_index=True)

    print(f"\nTotal comments fetched: {len(all_comments)}")
    print(all_comments.head())

    # Save to CSV
    # Add an 'id' column (starting from 1)
    all_comments.insert(0, "id", range(1, len(all_comments) + 1))
    filename = f"youtube/youtube_comments_{search_term.replace(' ', '_')}_{len(all_comments)}.csv"
    all_comments.to_csv(filename, index=False)

if __name__ == "__main__":
    main()