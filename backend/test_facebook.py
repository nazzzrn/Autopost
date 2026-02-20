import os
import logging
from dotenv import load_dotenv
from services import FacebookService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_facebook_publish():
    # Load .env
    dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    load_dotenv(dotenv_path, override=True)
    
    token = os.getenv("FACEBOOK_ACCESS_TOKEN")
    page_id = os.getenv("FACEBOOK_PAGE_ID")
    
    print(f"DEBUG: FACEBOOK_PAGE_ID: {page_id}")
    print(f"DEBUG: TOKEN_PREFIX: {token[:10] if token else 'NONE'}")
    print(f"DEBUG: TOKEN_SUFFIX: {token[-10:] if token else 'NONE'}")
    print(f"DEBUG: TOKEN_LENGTH: {len(token) if token else 0}")

    if not token or not page_id:
        print("ERROR: Missing Facebook credentials in .env")
        return

    service = FacebookService()
    
    image_url = "https://images.unsplash.com/photo-1542206395-9feb3edaa68d?w=600&q=80"
    caption = "This is a test post from AutoPost2 Facebook Service. 🚀"
    
    print("STATUS: Attempting to publish...")
    result = service.publish_post(image_path=image_url, caption=caption, schedule_time="")
    print(f"RESULT: {result}")

if __name__ == "__main__":
    test_facebook_publish()
