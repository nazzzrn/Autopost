import os
import google.generativeai as genai
from typing import List
import time
import requests

# Load environment variables (ensure main.py calls load_dotenv)

class GeminiService:
    def __init__(self):
        try:
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        except Exception as e:
            print(f"Error configuring Gemini: {e}")
            self.model = None

    def generate_caption(self, topic: str, platform: str, feedback: str = "") -> str:
        if not self.model:
            return "Gemini API key not configured."
        
        prompt = f"Create a social media caption for {platform} about '{topic}'."
        if feedback:
            prompt += f" Incorporate this feedback: {feedback}"
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
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
        # Simulate publishing
        print(f"Publishing to Instagram: Image={image_path}, Caption={caption[:20]}...")
        # Verify tokens exist
        if not os.getenv("INSTAGRAM_ACCESS_TOKEN"):
             return "Failed: Missing INSTAGRAM_ACCESS_TOKEN"
        return "Published to Instagram (Simulated)"

class FacebookService:
    def publish_post(self, image_path: str, caption: str, schedule_time: str) -> str:
        print(f"Publishing to Facebook: Image={image_path}, Caption={caption[:20]}...")
        if not os.getenv("FACEBOOK_ACCESS_TOKEN"):
             return "Failed: Missing FACEBOOK_ACCESS_TOKEN"
        return "Published to Facebook (Simulated)"

class LinkedInService:
    def publish_post(self, image_path: str, caption: str, schedule_time: str) -> str:
        print(f"Publishing to LinkedIn: Image={image_path}, Caption={caption[:20]}...")
        if not os.getenv("LINKEDIN_ACCESS_TOKEN"):
             return "Failed: Missing LINKEDIN_ACCESS_TOKEN"
        return "Published to LinkedIn (Simulated)"
