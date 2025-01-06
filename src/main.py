import argparse
from pathlib import Path

# Import different model handlers (you'll need to create these)
from models.qwen_handler import QwenHandler
from models.anthropic_handler import AnthropicHandler
from models.openAI_handler import ChatGPTHandler

def get_model_handler(model_name: str):
    model_handlers = {
        'qwen': QwenHandler,
        'anthropic': AnthropicHandler,
        'chatgpt': ChatGPTHandler
    }
    
    handler_class = model_handlers.get(model_name.lower())
    if not handler_class:
        raise ValueError(f"Unsupported model: {model_name}. Available models: {', '.join(model_handlers.keys())}")
    
    return handler_class()

def main(image_path: str, model_name: str):
    # Convert to absolute path if relative path is provided
    image_path = str(Path(image_path).absolute())
    
    # Get the appropriate model handler
    model_handler = get_model_handler(model_name)
    
    # Process the image using the selected model
    return model_handler.process_image(image_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analyze image for humor rating')
    parser.add_argument('image_path', type=str, help='Path to the image file to analyze')
    parser.add_argument('--model', type=str, default='qwen', 
                      help='Model to use for analysis (qwen, anthropic, or chatgpt)')
    
    args = parser.parse_args()
    result = main(args.image_path, args.model)
    print(result)