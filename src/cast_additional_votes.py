from .parser_router import main
import argparse
import json
from .dbSchema import cast_vote
from pathlib import Path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Cast additional votes for existing consensus')
    parser.add_argument('folder_path', type=str, help='Path to the image file(s) to analyze')
    parser.add_argument('--model', type=str, required=True,
                      help='Model to use for analysis (qwen, anthropic, or chatgpt)')
    parser.add_argument('--consensus-id', type=int, required=True,
                      help='Consensus ID to add votes to')
    parser.add_argument('--step', type=int, required=True,
                      help='Current step in the consensus process')
    
    args = parser.parse_args()
    folder_path = Path(args.folder_path)

    # Handle file or directory input
    if folder_path.is_file():
        image_paths = [folder_path]
    elif folder_path.is_dir():
        image_paths = []
        for ext in ['.jpg', '.jpeg', '.png', '.gif', '.JPG', '.JPEG', '.PNG', '.GIF']:
            image_paths.extend(folder_path.glob(f'*{ext}'))
    else:
        raise FileNotFoundError(f"Path not found: {folder_path}")

    # Process each image and cast votes
    for image_path in image_paths:
        try:
            result = main(str(image_path), args.model)
            result_dict = json.loads(result)
            
            # Cast vote in existing consensus
            cast_vote(
                image_path=str(image_path),
                model_name=args.model,
                consensus_id=args.consensus_id,
                step=args.step,
                choice=result_dict['choice'],
                description=result_dict['image_description']
            )
            
            print(f"\nVote cast for {image_path.name}:")
            print(json.dumps(result_dict, indent=2))
            
        except Exception as e:
            print(f"\nError processing {image_path}: {str(e)}")
            continue