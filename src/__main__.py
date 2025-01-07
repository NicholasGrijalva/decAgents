from .parser_router import main
import argparse
import json
from .dbSchema import save_analysis, init_db


if __name__ == "__main__":

    # create CLI parser object
    parser = argparse.ArgumentParser(description='Analyze image for humor rating')
    # add arguments, where you can later retrieve the values adjacent to it
    parser.add_argument('image_path', type=str, help='Path to the image file to analyze')
    parser.add_argument('--model', type=str, default='qwen', 
                      help='Model to use for analysis (qwen, anthropic, or chatgpt)')
    
    args = parser.parse_args()

    # take the related user inputs for the arguments and passes them in
    result = main(args.image_path, args.model)

    
    # Parse JSON result
    result_dict = json.loads(result)
    
    init_db()

    # Save to database
    save_analysis(args.image_path, args.model, result_dict)

    # result returns the json string thingy.
    print(result)


