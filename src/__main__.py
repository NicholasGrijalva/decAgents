from .parser_router import main
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analyze image for humor rating')
    parser.add_argument('image_path', type=str, help='Path to the image file to analyze')
    parser.add_argument('--model', type=str, default='qwen', 
                      help='Model to use for analysis (qwen, anthropic, or chatgpt)')
    
    args = parser.parse_args()
    result = main(args.image_path, args.model)
    print(result)