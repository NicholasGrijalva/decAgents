from pathlib import Path

def get_model_handler(model_name: str):
    #dynamically choose which agent to use 
    if model_name.lower() == 'qwen':
        #note: importing QwenHandler loads shards. be mindful and don't call unles necessary
        from .models.qwen_handler import QwenHandler
        return QwenHandler()
    elif model_name.lower() == 'anthropic':
        from .models.anthropic_handler import AnthropicHandler
        return AnthropicHandler()
    elif model_name.lower() == 'chatgpt':
        from .models.openAI_handler import ChatGPTHandler
        return ChatGPTHandler()
    else:
        raise ValueError(f"Unsupported model: {model_name}. Available models: qwen, anthropic, chatgpt")

def main(image_path: str, model_name: str):
    # Convert to absolute path if relative path is provided
    absolute_path = (Path(image_path).absolute())
    image_path = str(absolute_path)

    if not absolute_path.exists():
        raise FileNotFoundError(f"Image not found at path: {image_path}")
    
    # Get the appropriate model handler
    model_handler = get_model_handler(model_name)
    
    # Process the image using the selected model
    return model_handler.process_image(image_path)