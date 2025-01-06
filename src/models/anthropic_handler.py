from .base_handler import BaseModelHandler
from anthropic import Anthropic
from dotenv import load_dotenv
import os
import base64
from ..prompt import humor_prompt

class AnthropicHandler(BaseModelHandler):
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

    def process_image(self, image_path: str):
        # Initialize client with API key from .env
        client = Anthropic(api_key=self.api_key)
        
        # Read and encode image as base64
        with open(image_path, "rb") as img:
            image_data = img.read()
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": base64_image
                        }
                    },
                    {
                        "type": "text",
                        "text": humor_prompt
                    }
                ]
            }]
        )
        return response.content[0].text