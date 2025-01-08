from .base_handler import BaseModelHandler
from openai import OpenAI
from ..ad_prompt import ad_prompt
from dotenv import load_dotenv
import os
import json

class ChatGPTHandler(BaseModelHandler):
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
    def process_image(self, image_path: str):
        client = OpenAI()
        with open(image_path, "rb") as img:
            response = client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": ad_prompt},
                        {"type": "image_url", "image_url": {"url": img.read()}}
                    ]
                }]
            )
        
        # Ensure response is in correct JSON format
        try:
            raw_response = response.choices[0].message.content
            # If response isn't already JSON, try to parse it
            try:
                # Try parsing in case it's already JSON
                json.loads(raw_response)
                return raw_response
            except json.JSONDecodeError:
                # If not JSON, format it
                return json.dumps({
                    "image_description": raw_response,
                    "choice": 1  # Default to 1 if not specified in response
                })
        except Exception as e:
            raise ValueError(f"Failed to format response as JSON: {str(e)}")