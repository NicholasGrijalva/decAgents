from .parser_router import main
import argparse
import json
from .dbSchema import init_db, create_consensus, cast_vote
from pathlib import Path

if __name__ == "__main__":
    # create CLI parser object
    parser = argparse.ArgumentParser(description='Analyze images to choose best advertisement')
    parser.add_argument('folder_path', type=str, help='Path to the image file(s) to analyze')
    parser.add_argument('--model', type=str, default='qwen', 
                      help='Model to use for analysis (qwen, anthropic, or chatgpt)')
    
    args = parser.parse_args()
    folder_path = Path(args.folder_path)

    # Initialize Database and create new consensus
    init_db()
    consensus_id = create_consensus()
    
    # Handle file or directory input
    if folder_path.is_file():
        image_paths = [folder_path]
    elif folder_path.is_dir():
        image_paths = []
        for ext in ['.jpg', '.jpeg', '.png', '.gif', '.JPG', '.JPEG', '.PNG', '.GIF']:
            image_paths.extend(folder_path.glob(f'*{ext}'))
    else:
        raise FileNotFoundError(f"Path not found: {folder_path}")

    results = []
    best_image = None
    best_result = None

    # Process each image and cast votes
    for image_path in image_paths:
        try:
            # Process single image
            result = main(str(image_path), args.model)
            result_dict = json.loads(result)
            
            # Cast vote in consensus (step 0 for initial votes)
            cast_vote(
                image_path=str(image_path),
                model_name=args.model,
                consensus_id=consensus_id,
                step=0,
                choice=result_dict['choice'],
                description=result_dict['image_description']
            )

            # Store results and track best image
            result_dict["model"] = args.model
            result_dict["image_path"] = str(image_path)
            results.append(result_dict)
            
            # Update best image if this is chosen
            if result_dict['choice'] == 1:
                if best_image is not None:
                    print(f"\nWarning: Multiple images chosen as best ({best_image.name} and {image_path.name})")
                best_image = image_path
                best_result = result_dict
            
            
            # Print individual result
            print(f"\nAnalysis for {image_path.name}:")
            print(json.dumps(result_dict, indent=2))
            
        except Exception as e:
            print(f"\nError processing {image_path}: {str(e)}")
            continue

    # Print final results
    print(f"\nConsensus ID: {consensus_id}")
    if best_image:
        print("\n=== Best Advertisement Selected ===")
        print(f"Best Image: {best_image.name}")
        print("Analysis:")
        print(json.dumps(best_result, indent=2))
    else:
        print("\nNo image was selected as the best advertisement.")