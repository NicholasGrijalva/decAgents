from .base_handler import BaseModelHandler
from .qwen_Tools import create_image_message, process_message
from ..ad_prompt import ad_prompt
import json 

class QwenHandler(BaseModelHandler):
    def process_image(self, image_path: str):
        messages = create_image_message(image_path, ad_prompt)
        raw_response = process_message(messages)

        # Ensure response is in correct JSON format
        try:
            # Try parsing in case it's already JSON
            try:
                json.loads(raw_response)
                return raw_response
            except json.JSONDecodeError:
                # If not JSON, format it
                return json.dumps({
                    "image_description": raw_response,
                    "choice": 0  # Default to 0 if not specified in response
                })
        except Exception as e:
            raise ValueError(f"Failed to format response as JSON: {str(e)}")