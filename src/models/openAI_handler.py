from .base_handler import BaseModelHandler
from openai import OpenAI
from ..prompt import humor_prompt
from dotenv import load_dotenv
import os


class ChatGPTHandler(BaseModelHandler):
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
    def process_image(self, image_path: str):
        # One-shot implementation using GPT-4 Vision
        client = OpenAI()
        with open(image_path, "rb") as img:
            response = client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": humor_prompt},
                        {"type": "image_url", "image_url": {"url": img.read()}}
                    ]
                }]
            )
        return response.choices[0].message.content