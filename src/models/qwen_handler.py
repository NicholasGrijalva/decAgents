from .base_handler import BaseModelHandler
from .qwen_Tools import txt_to_message, create_image_message, process_message

class QwenHandler(BaseModelHandler):
    def process_image(self, image_path: str):
        prompt = (
            "Prompt: You are rating an image based on how funny it is. "
            "Take a detailed look at this image and, after analyzing it, "
            "provide a json object with the following fields:\n"
            "- image_description: a detailed description of the image and what makes it funny\n"
            "- rating: a rating from 1 to 10, where 1 is not funny and 10 is most funny"
        )
        messages = create_image_message(image_path, prompt)
        return process_message(messages)