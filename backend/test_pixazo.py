import os
import logging
import time
from dotenv import load_dotenv
from services import PixazoService

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

def test_pixazo():
    # Load .env
    dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    load_dotenv(dotenv_path)
    
    key = os.getenv("PIXAZO_KEY")
    if not key:
        logger.error("Missing PIXAZO_KEY in .env")
        return

    import requests
    headers = {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "Ocp-Apim-Subscription-Key": key
    }
    
    payload = {
        "prompt": "A majestic dragon sitting on a pile of gold, cinematic lighting, hyper-detailed, fantasy art",
        "num_steps": 4,
        "seed": 15,
        "height": 512,
        "width": 512
    }
    
    request_url = "https://gateway.pixazo.ai/flux-1-schnell/v1/getData"
    status_url = "https://gateway.pixazo.ai/flux-1-schnell/v1/checkStatus"

    start_time = time.time()
    logger.info(f"1. Sending request to {request_url}...")
    
    try:
        response = requests.post(request_url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        logger.info(f"Response data: {data}")

        # Case 1: Immediate output
        if "output" in data and data["output"]:
            duration = time.time() - start_time
            logger.info(f"✅ SUCCESS! (Immediate) Image URL: {data['output']} in {duration:.2f}s")
            return

        # Case 2: Request ID for polling
        request_id = data.get("requestId")
        if not request_id:
            logger.error("❌ FAILED! No output OR requestId in response.")
            return

        logger.info(f"2. Request queued. ID: {request_id}. Starting polling loop...")
        
        # User snippet used X-Secret-Key for status check
        poll_headers = headers.copy()
        poll_headers["X-Secret-Key"] = key
        if "Ocp-Apim-Subscription-Key" in poll_headers:
            del poll_headers["Ocp-Apim-Subscription-Key"]

        max_attempts = 20
        for attempt in range(max_attempts):
            logger.info(f"   Waiting 3 seconds before check {attempt + 1}...")
            time.sleep(3)
            logger.info(f"   Polling Attempt {attempt + 1}/{max_attempts}...")
            
            try:
                poll_response = requests.post(status_url, json={"requestId": request_id}, headers=poll_headers, timeout=20)
                poll_response.raise_for_status()
                poll_data = poll_response.json()
                logger.info(f"   Status: {poll_data.get('status')}")

                if poll_data.get("status") == "completed":
                    image_url = poll_data.get("output")
                    duration = time.time() - start_time
                    logger.info(f"✅ SUCCESS! Image URL: {image_url} in {duration:.2f}s")
                    return
                elif poll_data.get("status") == "failed":
                    logger.error(f"❌ FAILED! Job marked as failed: {poll_data}")
                    return
            except Exception as poll_err:
                logger.warning(f"   Polling error: {poll_err}")
        
        logger.error(f"❌ TIMEOUT! Reached max attempts ({max_attempts})")

    except Exception as e:
        logger.error(f"❌ ERROR! Request failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
             logger.error(f"Response: {e.response.text}")

if __name__ == "__main__":
    test_pixazo()
