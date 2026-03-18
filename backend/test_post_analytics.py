import os
import requests
from dotenv import load_dotenv

load_dotenv()

ig_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
ig_page_id = os.getenv("INSTAGRAM_PAGE_ID")
api_version = "v21.0"

def fetch_recent_posts_and_insights():
    if not ig_token or not ig_page_id:
        print("Missing INSTAGRAM_ACCESS_TOKEN or INSTAGRAM_PAGE_ID")
        return

    print("Fetching recent media IDs from Instagram...")
    url_media = f"https://graph.facebook.com/{api_version}/{ig_page_id}/media"
    
    try:
        resp = requests.get(url_media, params={"access_token": ig_token, "limit": 3})
        resp.raise_for_status()
        data = resp.json()
        
        media_list = data.get("data", [])
        if not media_list:
            print("No previous posts found on this Instagram account.")
            return
            
        print(f"Found {len(media_list)} recent posts. Fetching analytics for each...\n")
        
        for item in media_list:
            media_id = item["id"]
            print(f"--- Analytics for Media ID: {media_id} ---")
            
            # 1. Fetch likes and comments
            url_likes = f"https://graph.facebook.com/{api_version}/{media_id}"
            params_likes = {
                "fields": "like_count,comments_count,caption", 
                "access_token": ig_token
            }
            res_likes = requests.get(url_likes, params=params_likes)
            
            if res_likes.status_code == 200:
                likes_data = res_likes.json()
                caption = likes_data.get("caption", "No Caption").replace("\n", " ").encode('ascii', 'ignore').decode()
                print(f"Caption: {caption[:50]}...")
                print(f"Likes: {likes_data.get('like_count', 0)}")
                print(f"Comments: {likes_data.get('comments_count', 0)}")
            else:
                print("Failed to fetch likes/comments:", res_likes.json())

            # 2. Fetch reach & engagement
            url_ins = f"https://graph.facebook.com/{api_version}/{media_id}/insights"
            params_ins = {
                "metric": "reach,saved", 
                "access_token": ig_token
            }
            res_ins = requests.get(url_ins, params=params_ins)
            
            if res_ins.status_code == 200:
                ins_data = res_ins.json().get("data", [])
                for metric in ins_data:
                    name = metric.get("name")
                    values = metric.get("values", [])
                    val = values[0].get("value", 0) if values else 0
                    print(f"{name.capitalize()}: {val}")
            else:
                print("Failed to fetch reach/impressions:", res_ins.json())
                
            print("\n")

    except Exception as e:
        print("Error connecting to Graph API:", e)

if __name__ == "__main__":
    fetch_recent_posts_and_insights()
