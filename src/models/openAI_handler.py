from .base_handler import BaseModelHandler
from openai import OpenAI

class ChatGPTHandler(BaseModelHandler):
    def process_image(self, image_path: str):
        # One-shot implementation using GPT-4 Vision
        client = OpenAI()
        with open(image_path, "rb") as img:
            response = client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyze this image for humor"},
                        {"type": "image_url", "image_url": {"url": img.read()}}
                    ]
                }]
            )
        return response.choices[0].message.content