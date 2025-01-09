from pathlib import Path
import json

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
    # First part remains the same - path validation
    absolute_path = (Path(image_path).absolute())
    image_path = str(absolute_path)

    if not absolute_path.exists():
        raise FileNotFoundError(f"Image not found at path: {image_path}")
    
    # Get the appropriate model handler - this stays the same
    model_handler = get_model_handler(model_name)
    
    # Process the image and get raw result
    raw_result = model_handler.process_image(image_path)
    
    # Parse the JSON result and convert choice to binary
    try:
        result_dict = json.loads(raw_result)
        # Convert any choice value to binary (1 if the model chose this image, 0 otherwise)
        result_dict['choice'] = 1 if result_dict['choice'] == 1 else 0
        # Convert back to JSON string
        return json.dumps(result_dict)
    except json.JSONDecodeError:
        raise ValueError(f"Model returned invalid JSON: {raw_result}")