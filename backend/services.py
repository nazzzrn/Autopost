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

    def generate_caption(self, topic: str, platform: str, feedback: str = "") -> List[str]:
        if not self.model:
            logger.error("GeminiService: API key not configured.")
            return ["Gemini API key not configured."]
        
        prompt = f"""
        Create 3 distinct social media captions for {platform} about '{topic}'.
        
        Return ONLY a raw JSON list of strings, like this:
        ["Caption option 1...", "Caption option 2...", "Caption option 3..."]
        
        Do not include markdown formatting like ```json.
        """
        if feedback:
            prompt += f" Incorporate this feedback: {feedback}"
        
        try:
            response = self.model.generate_content(prompt)
            logger.info(f"GeminiService: Captions generated for {platform}.")
            
            # Clean up response
            text = response.text.strip()
            import re
            import json
            text = re.sub(r"```json", "", text)
            text = re.sub(r"```", "", text)
            text = text.strip()
            
            try:
                captions = json.loads(text)
                if isinstance(captions, list):
                    return captions[:3] # Ensure max 3
                return [text] # Fallback
            except json.JSONDecodeError:
                logger.warning("GeminiService: Failed to parse JSON captions, returning raw text as single option.")
                return [text]
                
        except Exception as e:
            logger.error(f"GeminiService: Error generating caption: {e}")
            return [f"Error generating caption: {e}"]

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

    def generate_image(self, topic: str, feedback: str = "") -> str:
        if not self.model:
            return "Gemini API key not configured."
            
        # Use Gemini to generate a high-quality prompt for Flux 1 Schnell
        refinement_prompt = f"""
        Create a concise, highly descriptive image generation prompt for Flux 1 Schnell about '{topic}'.
        Describe the scene clearly, focusing on subjects, style, and lighting.
        Input: {topic}
        {f"Feedback to incorporate: {feedback}" if feedback else ""}
        
        Return ONLY the refined prompt text. Keep it under 100 words.
        """
        
        try:
            prompt_response = self.model.generate_content(refinement_prompt)
            refined_prompt = prompt_response.text.strip()
            logger.info(f"GeminiService: Refined prompt for Pixazo: {refined_prompt[:50]}...")
            
            # Now call Pixazo
            pixazo = PixazoService()
            image_url = pixazo.generate_image(refined_prompt)
            
            if image_url:
                return image_url
            
            # Fallback
            return mock_generate_image(f"Pixazo failed: {topic}")
            
        except Exception as e:
            logger.error(f"GeminiService: Error in generate_image (Pixazo path): {e}")
            return mock_generate_image(f"Error {e}")

class PixazoService:
    def __init__(self):
        self.api_key = os.getenv("PIXAZO_KEY")
        self.request_url = "https://gateway.pixazo.ai/flux-1-schnell/v1/getData"
        self.result_url = "https://gateway.pixazo.ai/flux-1-schnell/v1/checkStatus"
        self.secret_key = os.getenv("PIXAZO_KEY") # User snippet mentions X-Secret-Key in generic, but also Key in others. Assuming subscription key works.
        
    def generate_image(self, prompt: str) -> str:
        if not self.api_key:
            logger.error("PixazoService: Missing PIXAZO_KEY in .env")
            return None
            
        headers = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "Ocp-Apim-Subscription-Key": self.api_key
        }
        
        payload = {
            "prompt": prompt,
            "num_steps": 4,
            "seed": 15,
            "height": 512,
            "width": 512
        }
        
        try:
            logger.info(f"PixazoService: Sending request for prompt: {prompt[:50]}...")
            response = requests.post(self.request_url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            # Check if output is immediate
            image_url = data.get("output")
            if image_url:
                logger.info(f"PixazoService: Immediate output received: {image_url}")
                return image_url
            
            request_id = data.get("requestId")
            if not request_id:
                logger.error(f"PixazoService: No output or requestId in response: {data}")
                return None
                
            logger.info(f"PixazoService: Request in progress. ID: {request_id}. Polling...")
            
            # Update headers for polling if needed (user snippet showed X-Secret-Key)
            poll_headers = headers.copy()
            if "Ocp-Apim-Subscription-Key" in poll_headers:
                poll_headers["X-Secret-Key"] = poll_headers.pop("Ocp-Apim-Subscription-Key")

            # Polling logic
            max_attempts = 10
            for attempt in range(max_attempts):
                time.sleep(2) # Schnell is faster
                logger.info(f"PixazoService: Polling status (Attempt {attempt+1}/{max_attempts})...")
                
                res_payload = {"requestId": request_id}
                try:
                    res_response = requests.post(self.result_url, json=res_payload, headers=poll_headers, timeout=30)
                    res_response.raise_for_status()
                    res_data = res_response.json()
                except Exception as poll_e:
                    logger.warning(f"PixazoService: Polling error on attempt {attempt+1}: {poll_e}")
                    continue
                
                status = res_data.get("status", "").lower()
                if status == "completed":
                    image_url = res_data.get("output")
                    if image_url:
                        logger.info(f"PixazoService: Image generation completed. URL: {image_url}")
                        return image_url
                elif status == "failed":
                    logger.error(f"PixazoService: Generation failed for ID {request_id}")
                    return None
                
            logger.warning(f"PixazoService: Timeout reached for ID {request_id}")
            return None
            
        except requests.exceptions.ConnectionError as ce:
            logger.error(f"PixazoService: Connection Error. The machine actively refused it. Check your internet/firewall: {ce}")
            return None
        except Exception as e:
            logger.error(f"PixazoService: Error: {e}")
            return None

# Placeholder for image generation fallback
def mock_generate_image(description: str) -> str:
    # Use a high-quality static image from Unsplash as a robust fallback.
    # Placeholder URLs are often rejected by Instagram/Facebook filters.
    logger.info(f"Using fallback image for: {description[:30]}...")
    return "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&q=80&w=1200"


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
        
        url = f"https://graph.facebook.com/v21.0/{ig_user_id}/media"
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
            publish_url = f"https://graph.facebook.com/v21.0/{ig_user_id}/media_publish"
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
        logger.info(f"FacebookService: Publishing post. Image={image_path}")
        
        access_token = os.getenv("FACEBOOK_ACCESS_TOKEN")
        page_id = os.getenv("FACEBOOK_PAGE_ID")
        
        if not access_token or not page_id:
             logger.error("FacebookService: Missing credentials")
             return "Failed: Missing FACEBOOK_ACCESS_TOKEN or FACEBOOK_PAGE_ID"

        # Handle local/blob images
        final_image_url = image_path
        if image_path.startswith("blob:") or image_path.startswith("data:"):
            logger.info("FacebookService: Detected local/blob image. Uploading to public host...")
            host_service = FreeImageHostService()
            public_url = host_service.upload_image(image_path)
            if public_url:
                final_image_url = public_url
            else:
                return "Failed: Could not upload local image to public host."

        # Facebook Page API - Post photo to feed
        # Using /feed with link + message is often more robust than /photos for newer tokens
        url = f"https://graph.facebook.com/v21.0/{page_id}/feed"
        payload = {
            "link": final_image_url,
            "message": caption,
            "access_token": access_token
        }
        
        try:
            response = requests.post(url, data=payload)
            response.raise_for_status()
            result = response.json()
            
            if "id" in result:
                logger.info(f"FacebookService: Successfully published. ID: {result['id']}")
                return "Published to Facebook"
            else:
                logger.error(f"FacebookService: Failed to publish. Response: {result}")
                return "Failed: Could not publish"
                
        except requests.exceptions.RequestException as e:
            logger.error(f"FacebookService: API Error: {e}")
            if e.response is not None:
                return f"Failed: API Error - {e.response.text}"
            return f"Failed: API Error - {str(e)}"
        except Exception as e:
            logger.error(f"FacebookService: Unexpected error: {e}")
            return f"Failed: {str(e)}"

class LinkedInService:
    def publish_post(self, image_path: str, caption: str, schedule_time: str) -> str:
        logger.info(f"LinkedInService: Publishing post. Image={image_path}, Caption={caption[:20]}...")
        if not os.getenv("LINKEDIN_ACCESS_TOKEN"):
             logger.error("LinkedInService: Missing LINKEDIN_ACCESS_TOKEN")
             return "Failed: Missing LINKEDIN_ACCESS_TOKEN"
        return "Published to LinkedIn (Simulated)"
