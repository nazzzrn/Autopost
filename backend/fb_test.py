import os
import requests
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")

GRAPH_API_VERSION = "v24.0"
GRAPH_API_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"


def publish_test_post():
    """
    Publishes a test post to Facebook page
    """

    if not PAGE_ID or not ACCESS_TOKEN:
        print("❌ ERROR: Missing FACEBOOK_PAGE_ID or FACEBOOK_ACCESS_TOKEN in .env")
        return

    url = f"{GRAPH_API_URL}/{PAGE_ID}/feed"

    message = f"""
✅ FastAPI Facebook publish test successful!

Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

This post was published automatically using Graph API.
"""

    payload = {
        "message": message,
        "access_token": ACCESS_TOKEN
    }

    try:
        print("🚀 Publishing post to Facebook...")

        response = requests.post(url, data=payload)

        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS: Post published")
            print("Post ID:", result.get("id"))

        else:
            print("❌ FAILED")
            print("Status Code:", response.status_code)
            print("Response:", response.text)

    except Exception as e:
        print("❌ EXCEPTION OCCURRED")
        print(str(e))


if __name__ == "__main__":
    publish_test_post()
