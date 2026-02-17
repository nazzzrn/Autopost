import os
import logging
from dotenv import load_dotenv
from services import InstagramService

# Configure logging to see the output
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_instagram_publish():
    # Load environment variables from the root .env file
    # Assuming this script is run from backend/ or root, we might need to adjust path
    # But usually python-dotenv finds it if it's in parent or current.
    # explicit path to be sure:
    dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    load_dotenv(dotenv_path)
    
    logger.info("Loaded .env file")
    
    # Check credentials
    token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    page_id = os.getenv("INSTAGRAM_PAGE_ID")
    
    if not token or not page_id:
        logger.error("Missing Instagram credentials in .env")
        return

    logger.info(f"Page ID: {page_id}")
    logger.info(f"Access Token (First 10): {token[:10]}...") 
    logger.info(f"Access Token (Last 10): ...{token[-10:]}")
    logger.info(f"Access Token Length: {len(token)}")

    service = InstagramService()
    
    # Test Data
    # Use a public image URL for simplicity to test the Instagram part directly
    # OR use a local path to test the FreeImageHost integration too.
    # Let's test the full flow with a public URL first to be safe, 
    # then maybe a "mock" local file string if needed.
    # Actually, let's use a known public image to ensure Instagram accepts it.
    image_url = "https://images.unsplash.com/photo-1542206395-9feb3edaa68d?w=600&q=80"
    caption = "This is a test post from the AutoPost2 backend verification script. 🤖 #testing #automation"
    
    logger.info("Attempting to publish...")
    result = service.publish_post(image_path=image_url, caption=caption, schedule_time="")
    
    logger.info(f"Result: {result}")

if __name__ == "__main__":
    test_instagram_publish()
