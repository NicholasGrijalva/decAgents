from .base_handler import BaseModelHandler
from anthropic import Anthropic
from dotenv import load_dotenv
import os
import base64
from ..ad_prompt import ad_prompt

class AnthropicHandler(BaseModelHandler):
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

    def process_image(self, image_path: str):
        client = Anthropic(api_key=self.api_key)
        
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
                            "media_type": self._get_media_type(image_path),
                            "data": base64_image
                        }
                    },
                    {
                        "type": "text",
                        "text": ad_prompt
                    }
                ]
            }]
        )
        
        # Ensure response is in correct JSON format
        try:
            # If response isn't already JSON, format it as JSON
            import json
            return json.dumps({
                "image_description": response.content[0].text,
                "choice": 1  # You might want to extract this from the response
            })
        except Exception as e:
            raise ValueError(f"Failed to format response as JSON: {str(e)}")

    def _get_media_type(self, image_path: str) -> str:
        """Determine the correct media type based on file extension"""
        ext = image_path.lower().split('.')[-1]
        media_types = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif'
        }
        return media_types.get(ext, 'image/jpeg')