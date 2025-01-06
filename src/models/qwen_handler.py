from .base_handler import BaseModelHandler
from .qwen_Tools import create_image_message, process_message
from src.prompt import humor_prompt

class QwenHandler(BaseModelHandler):
    def process_image(self, image_path: str):
        messages = create_image_message(image_path, humor_prompt)
        return process_message(messages)