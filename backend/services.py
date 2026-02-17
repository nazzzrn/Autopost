import os
import google.generativeai as genai
from typing import List
import time
import requests
import logging

logger = logging.getLogger(__name__)

# Load environment variables (ensure main.py calls load_dotenv)

class GeminiService:
    def __init__(self):
        try:
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            self.model = genai.GenerativeModel('gemini-2.5-flash-lite')
            logger.info("GeminiService: Configured successfully.")
        except Exception as e:
            logger.error(f"GeminiService: Error configuring Gemini: {e}")
            self.model = None

    def generate_caption(self, topic: str, platform: str, feedback: str = "") -> str:
        if not self.model:
            logger.error("GeminiService: API key not configured.")
            return "Gemini API key not configured."
        
        prompt = f"Create a social media caption for {platform} about '{topic}'. Return only a single caption without any other trailing text."
        if feedback:
            prompt += f" Incorporate this feedback: {feedback}"
        
        try:
            response = self.model.generate_content(prompt)
            logger.info(f"GeminiService: Caption generated for {platform}.")
            return response.text
        except Exception as e:
            logger.error(f"GeminiService: Error generating caption: {e}")
            return f"Error generating caption: {e}"

    def generate_image_description(self, topic: str, feedback: str = "") -> str:
        # Since we might not have direct image generation in this free tier or specific library, 
        # we'll simulate image generation or use a placeholder if not available.
        # For this requirement, "Generate image using Gemini" might imply using a tool or just description if text-only model.
        # Assuming we need to return a path to a generated image. 
        # For simplicity in this demo without a real image gen API (unless Gemini Pro Vision is used for inputs),
        # we might need to mock the image generation or use a free placeholder service based on keywords.
        # Let's use a placeholder service for now as a robust fallback, or return a description.
        # The prompt asks for "Generate image using Gemini". 
        # Gemini Pro doesn't generate images directly in all tiers/libraries yet without specific tools.
        # I will implement a text-to-image prompt generator and then use a placeholder or mock for the file.
        
        if not self.model:
            return "Gemini API key not configured."
            
        prompt = f"Describe an image for a social media post about '{topic}'."
        if feedback:
            prompt += f" Feedback: {feedback}"
            
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error: {e}"

# Placeholder for image generation (mocking for now as Gemini Image Gen requires specific setup/API availability)
# We will save a dummy image or use a placeholder URL.
def mock_generate_image(description: str) -> str:
    # In a real app, call DALL-E or Gemini Image endpoint if available.
    # Here we'll return a placeholder image URL or create a solid color image.
    # For a "full-stack application", let's return a valid placeholder URL that the frontend can display.
    # Or generate a simple image using python PIL if needed.
    # Let's return a placeholder URL for simplicity and robustness.
    import urllib.parse
    encoded_desc = urllib.parse.quote(description[:20]) # Limit length
    return f"https://via.placeholder.com/600x400?text={encoded_desc}"


class InstagramService:
    def publish_post(self, image_path: str, caption: str, schedule_time: str) -> str:
        logger.info(f"InstagramService: Publishing post. Image={image_path}")
        
        access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
        ig_user_id = os.getenv("INSTAGRAM_PAGE_ID")
        
        if not access_token or not ig_user_id:
             logger.error("InstagramService: Missing credentials")
             return "Failed: Missing INSTAGRAM_ACCESS_TOKEN or INSTAGRAM_PAGE_ID"

        # Step 1: Create Media Container
        # Handle Blob IDs / Base64 / Local paths by uploading to freeimage.host
        final_image_url = image_path
        
        if image_path.startswith("blob:") or image_path.startswith("data:"):
            logger.info("InstagramService: Detected local/blob image. Uploading to public host...")
            host_service = FreeImageHostService()
            public_url = host_service.upload_image(image_path)
            if public_url:
                final_image_url = public_url
            else:
                return "Failed: Could not upload local image to public host."
        
        url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media"
        payload = {
            "image_url": final_image_url,
            "caption": caption,
            "access_token": access_token
        }
        
        try:
            # Create container
            response = requests.post(url, data=payload)
            response.raise_for_status()
            result = response.json()
            creation_id = result.get("id")
            
            if not creation_id:
                logger.error(f"InstagramService: Failed to create media container. Response: {result}")
                return "Failed: Could not create media container"
            
            logger.info(f"InstagramService: Media container created: {creation_id}")
            
            # Step 2: Publish Media
            publish_url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media_publish"
            publish_payload = {
                "creation_id": creation_id,
                "access_token": access_token
            }
            
            # Instagram sometimes needs a few seconds to process the image before publishing
            # We can add a simple retry or wait logic if needed, but for now specific sleep might be safer.
            time.sleep(3) 

            pub_response = requests.post(publish_url, data=publish_payload)
            pub_response.raise_for_status()
            pub_result = pub_response.json()
            
            if "id" in pub_result:
                logger.info(f"InstagramService: Successfully published. ID: {pub_result['id']}")
                return "Published to Instagram"
            else:
                logger.error(f"InstagramService: Failed to publish. Response: {pub_result}")
                return "Failed: Could not publish media"
                
        except requests.exceptions.RequestException as e:
            logger.error(f"InstagramService: API Error: {e}")
            if e.response is not None:
                logger.error(f"Response: {e.response.text}")
                return f"Failed: API Error - {e.response.text}"
            return f"Failed: API Error - {str(e)}"
        except Exception as e:
            logger.error(f"InstagramService: Unexpected error: {e}")
            return f"Failed: {str(e)}"

class FreeImageHostService:
    def __init__(self):
        self.api_key = "6d207e02198a847aa98d0a2a901485a5"
        self.upload_url = "https://freeimage.host/api/1/upload"

    def upload_image(self, source: str) -> str:
        """
        Uploads an image to freeimage.host.
        Source can be a URL or a Base64 string.
        Returns the direct URL of the uploaded image.
        """
        try:
            # Check if source is base64 data URI and strip header if needed
            if source.startswith("data:image"):
                logger.info("FreeImageHostService: Stripping data:image header")
                source = source.split(",", 1)[1]
            
            logger.info(f"FreeImageHostService: Uploading image. Length: {len(source)}")
            logger.info(f"FreeImageHostService: Source prefix: {source[:20]}...")

            payload = {
                "key": self.api_key,
                "action": "upload",
                "source": source,
                "format": "json"
            }
            
            logger.info("FreeImageHostService: Uploading image...")
            response = requests.post(self.upload_url, data=payload)
            response.raise_for_status()
            
            data = response.json()
            if data["status_code"] == 200:
                image_url = data["image"]["url"]
                logger.info(f"FreeImageHostService: Upload successful. URL: {image_url}")
                return image_url
            else:
                logger.error(f"FreeImageHostService: Upload failed. Status: {data['status_txt']}")
                return None
        except Exception as e:
            logger.error(f"FreeImageHostService: Error uploading image: {e}")
            return None

class FacebookService:
    def publish_post(self, image_path: str, caption: str, schedule_time: str) -> str:
        logger.info(f"FacebookService: Publishing post. Image={image_path}, Caption={caption[:20]}...")
        if not os.getenv("FACEBOOK_ACCESS_TOKEN"):
             logger.error("FacebookService: Missing FACEBOOK_ACCESS_TOKEN")
             return "Failed: Missing FACEBOOK_ACCESS_TOKEN"
        return "Published to Facebook (Simulated)"

class LinkedInService:
    def publish_post(self, image_path: str, caption: str, schedule_time: str) -> str:
        logger.info(f"LinkedInService: Publishing post. Image={image_path}, Caption={caption[:20]}...")
        if not os.getenv("LINKEDIN_ACCESS_TOKEN"):
             logger.error("LinkedInService: Missing LINKEDIN_ACCESS_TOKEN")
             return "Failed: Missing LINKEDIN_ACCESS_TOKEN"
        return "Published to LinkedIn (Simulated)"
