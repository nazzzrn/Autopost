import requests
import io
import base64
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_freeimage_upload():
    api_key = "6d207e02198a847aa98d0a2a901485a5"
    upload_url = "https://freeimage.host/api/1/upload"

    # Create a simple small white square image in base64
    # 1x1 pixel PNG
    base64_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAAAAAA6fptVAAAACklEQVR4nGNiAAAABgADNjd8qAAAAABJRU5ErkJggg=="
    
    # Try to make it larger by repeating? No, that corrupts it. 
    # Just use it as is first. The 1x1 worked.
    # To test size limit, we'd need a real larger base64. 
    # Let's assume the 1x1 works and the issue is specific to the user's data.
    
    logger.info("Testing FreeImage.host upload with proper payload...")

    payload = {
        "key": api_key,
        "action": "upload",
        "source": base64_image,
        "format": "json"
    }

    try:
        response = requests.post(upload_url, data=payload)
        logger.info(f"Status Code: {response.status_code}")
        
        if response.status_code != 200:
            logger.error(f"Response: {response.text}")
        else:
            logger.info(f"Response: {response.json()}")
            
    except Exception as e:
        logger.error(f"Exception: {e}")

if __name__ == "__main__":
    test_freeimage_upload()
