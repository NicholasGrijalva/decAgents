print("Starting main module execution...")
import argparse
import json
from .parser_router import main
from .dbSchema import init_db, create_consensus, cast_vote
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import List, Dict, Tuple

class ConsensusVoting:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        
    def get_current_votes(self, consensus_id: int, step: int) -> Tuple[List[str], List[str], np.ndarray]:
        """
        Retrieve current votes for a specific consensus round and step.
        Returns agent_ids, image_paths, and vote matrix.
        """
        conn = sqlite3.connect(self.db_path)
        try:
            # Get unique agents and images for this consensus
            cursor = conn.cursor()
            
            # Get all agents who have voted in this consensus
            cursor.execute("""
                SELECT DISTINCT m.model_id, m.model_name 
                FROM votes v
                JOIN models m ON v.agent_id = m.model_id
                WHERE v.consensus_id = ? AND v.step = ?
                ORDER BY m.model_id
            """, (consensus_id, step))
            agents = cursor.fetchall()
            
            # Get all images in this consensus
            cursor.execute("""
                SELECT DISTINCT i.image_id, i.image_path
                FROM votes v
                JOIN images i ON v.image_id = i.image_id
                WHERE v.consensus_id = ? AND v.step = ?
                ORDER BY i.image_id
            """, (consensus_id, step))
            images = cursor.fetchall()
            
            # Create vote matrix
            vote_matrix = np.zeros((len(agents), len(images)))
            
            # Fill vote matrix
            for i, (agent_id, _) in enumerate(agents):
                for j, (image_id, _) in enumerate(images):
                    cursor.execute("""
                        SELECT choice 
                        FROM votes 
                        WHERE consensus_id = ? AND step = ? AND agent_id = ? AND image_id = ?
                    """, (consensus_id, step, agent_id, image_id))
                    result = cursor.fetchone()
                    if result:
                        vote_matrix[i, j] = result[0]
            
            return (
                [name for _, name in agents],
                [path for _, path in images],
                vote_matrix
            )
            
        finally:
            conn.close()

    def update_consensus(self, consensus_id: int, step: int, 
                        vote_matrix: np.ndarray, 
                        agents: List[str], 
                        image_paths: List[str],
                        influence_weight: float = 0.3) -> np.ndarray:
        """
        Update votes based on neighboring agents' influence.
        Returns the new vote matrix.
        """
        num_agents = len(agents)
        new_votes = np.zeros_like(vote_matrix)
        
        for i in range(num_agents):
            # Calculate influenced votes
            if i == 0:  # First agent
                neighbors = vote_matrix[i+1]
                new_votes[i] = (1 - influence_weight) * vote_matrix[i] + influence_weight * neighbors
            elif i == num_agents - 1:  # Last agent
                neighbors = vote_matrix[i-1]
                new_votes[i] = (1 - influence_weight) * vote_matrix[i] + influence_weight * neighbors
            else:  # Middle agents
                neighbors = (vote_matrix[i-1] + vote_matrix[i+1]) / 2
                new_votes[i] = (1 - influence_weight) * vote_matrix[i] + influence_weight * neighbors
        
        # Store updated votes in database
        self._store_updated_votes(consensus_id, step + 1, new_votes, agents, image_paths)
        
        return new_votes

    def _store_updated_votes(self, consensus_id: int, step: int, 
                           vote_matrix: np.ndarray, 
                           agents: List[str], 
                           image_paths: List[str]) -> None:
        """Store the updated votes in the database"""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            # Get agent_ids and image_ids
            for i, agent_name in enumerate(agents):
                cursor.execute("SELECT model_id FROM models WHERE model_name = ?", (agent_name,))
                agent_id = cursor.fetchone()[0]
                
                for j, image_path in enumerate(image_paths):
                    cursor.execute("SELECT image_id FROM images WHERE image_path = ?", (image_path,))
                    image_id = cursor.fetchone()[0]
                    
                    # Insert new vote
                    cursor.execute("""
                        INSERT INTO votes (agent_id, image_id, consensus_id, step, choice, description)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (agent_id, image_id, consensus_id, step, float(vote_matrix[i, j]), 
                         f"Consensus step {step} update"))
            
            # Update consensus current_step
            cursor.execute("""
                UPDATE consensus 
                SET current_step = ?
                WHERE consensus_id = ?
            """, (step, consensus_id))
            
            conn.commit()
        finally:
            conn.close()

    def plot_convergence(self, consensus_id: int, max_step: int = None):
        """Plot the convergence of votes over steps"""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            if max_step is None:
                cursor.execute("SELECT MAX(step) FROM votes WHERE consensus_id = ?", (consensus_id,))
                max_step = cursor.fetchone()[0]
            
            plt.figure(figsize=(12, 8))
            
            # Get all images
            cursor.execute("""
                SELECT DISTINCT i.image_id, i.image_path
                FROM votes v
                JOIN images i ON v.image_id = i.image_id
                WHERE v.consensus_id = ?
                ORDER BY i.image_id
            """, (consensus_id,))
            images = cursor.fetchall()
            
            # Plot votes for each image
            for image_id, image_path in images:
                votes = []
                for step in range(max_step + 1):
                    cursor.execute("""
                        SELECT AVG(choice)
                        FROM votes
                        WHERE consensus_id = ? AND step = ? AND image_id = ?
                    """, (consensus_id, step, image_id))
                    avg_vote = cursor.fetchone()[0]
                    votes.append(avg_vote)
                
                plt.plot(range(max_step + 1), votes, 
                        label=Path(image_path).name, 
                        marker='o')
            
            plt.xlabel("Consensus Step")
            plt.ylabel("Average Vote")
            plt.title(f"Vote Convergence for Consensus #{consensus_id}")
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.grid(True)
            plt.tight_layout()
            plt.show()
            
        finally:
            conn.close()

def run_consensus_round(db_path: Path, consensus_id: int, 
                       max_iterations: int = 10, 
                       convergence_threshold: float = 0.01) -> Dict:
    """
    Run a complete consensus round and return the final results.
    """
    consensus = ConsensusVoting(db_path)
    
    # Get initial votes
    agents, image_paths, vote_matrix = consensus.get_current_votes(consensus_id, 0)
    
    for step in range(max_iterations):
        # Update votes
        new_votes = consensus.update_consensus(consensus_id, step, vote_matrix, agents, image_paths)
        
        # Check for convergence
        if np.max(np.abs(new_votes - vote_matrix)) < convergence_threshold:
            print(f"Converged after {step + 1} iterations")
            break
            
        vote_matrix = new_votes
    
    # Plot convergence
    consensus.plot_convergence(consensus_id)
    
    # Return final results
    final_scores = np.mean(vote_matrix, axis=0)
    best_image_idx = np.argmax(final_scores)
    
    return {
        "consensus_id": consensus_id,
        "best_image": image_paths[best_image_idx],
        "final_scores": dict(zip(image_paths, final_scores.tolist())),
        "iterations": step + 1
    }

if __name__ == "__main__":
    # create CLI parser object
    parser = argparse.ArgumentParser(description='Analyze images to choose best advertisement')
    parser.add_argument('folder_path', type=str, help='Path to the image file(s) to analyze')
    parser.add_argument('--model', type=str, default='qwen', 
                      help='Model to use for analysis (qwen, anthropic, or chatgpt)')
    parser.add_argument('--run-consensus', action='store_true',
                      help='Run consensus algorithm with existing votes')
    
    args = parser.parse_args()
    folder_path = Path(args.folder_path)

    # Initialize Database and create new consensus if not running existing consensus
    init_db()
    if not args.run_consensus:
        consensus_id = create_consensus()
        print(f"Created new consensus with ID: {consensus_id}")
    
    # Handle file or directory input
    if folder_path.is_file():
        image_paths = [folder_path]
    elif folder_path.is_dir():
        image_paths = []
        for ext in ['.jpg', '.jpeg', '.png', '.gif']:
            image_paths.extend(folder_path.glob(f'*{ext}'))
        print(f"Found {len(image_paths)} images in directory")
    else:
        raise FileNotFoundError(f"Path not found: {folder_path}")

    if not args.run_consensus:
        # Process each image and cast initial votes
        for image_path in image_paths:
            try:
                print(f"\nProcessing {image_path.name}...")
                result = main(str(image_path), args.model)
                result_dict = json.loads(result)
                
                cast_vote(
                    image_path=str(image_path),
                    model_name=args.model,
                    consensus_id=consensus_id,
                    step=0,
                    choice=result_dict['choice'],
                    description=result_dict['image_description']
                )
                
                print("Vote cast!")
                print(json.dumps(result_dict, indent=2))
                
            except Exception as e:
                print(f"Error processing {image_path}: {str(e)}")
                continue
    else:
        # Run consensus algorithm on existing votes
        print("\nRunning consensus algorithm...")
        db_path = Path(__file__).parent / 'image_analysis.db'
        
        # Get most recent consensus_id if not provided
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(consensus_id) FROM consensus")
        consensus_id = cursor.fetchone()[0]
        conn.close()
        
        final_results = run_consensus_round(db_path, consensus_id)
        
        print("\n=== Consensus Results ===")
        print(f"Best Image: {Path(final_results['best_image']).name}")
        print("\nFinal Scores:")
        for image_path, score in final_results['final_scores'].items():
            print(f"{Path(image_path).name}: {score:.3f}")
        print(f"\nConverged after {final_results['iterations']} iterations")