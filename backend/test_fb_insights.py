import os
import requests
from dotenv import load_dotenv

load_dotenv()

fb_token = os.getenv("FACEBOOK_ACCESS_TOKEN")
fb_page_id = os.getenv("FACEBOOK_PAGE_ID")
ig_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
ig_page_id = os.getenv("INSTAGRAM_PAGE_ID")

def test_fb():
    metrics = ["page_impressions", "page_post_engagements", "page_fan_adds"]
    for m in metrics:
        url = f"https://graph.facebook.com/v21.0/{fb_page_id}/insights"
        params = {
            "metric": m,
            "period": "day",
            "access_token": fb_token,
        }
def test_ig():
    url = f"https://graph.facebook.com/v21.0/{ig_page_id}/insights"
    params1 = {
        "metric": "reach,accounts_engaged",
        "period": "day",
        "access_token": ig_token,
    }
    resp1 = requests.get(url, params=params1)
    print("IG ERROR without total_value:", resp1.json())
    
    params2 = {
        "metric": "reach,accounts_engaged",
        "period": "day",
        "metric_type": "total_value",
        "access_token": ig_token,
    }
    resp2 = requests.get(url, params=params2)
    print("IG ERROR with total_value:", resp2.json())

test_ig()
