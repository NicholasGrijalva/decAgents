from pathlib import Path

def get_model_handler(model_name: str):
    """Dynamically import and return the appropriate model handler"""
    if model_name.lower() == 'qwen':
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
    image_path = str(Path(image_path).absolute())
    
    # Get the appropriate model handler
    model_handler = get_model_handler(model_name)
    
    # Process the image using the selected model
    return model_handler.process_image(image_path)