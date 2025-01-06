from .base_handler import BaseModelHandler
from anthropic import Anthropic
from dotenv import load_dotenv
import os

class AnthropicHandler(BaseModelHandler):
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

    def process_image(self, image_path: str):
        # Initialize client with API key from .env
        client = Anthropic(api_key=self.api_key)
        with open(image_path, "rb") as img:
            response = client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {"type": "base64", "data": img.read()}
                        },
                        {
                            "type": "text",
                            "text": "Analyze this image for humor"
                        }
                    ]
                }]
            )
        return response.content