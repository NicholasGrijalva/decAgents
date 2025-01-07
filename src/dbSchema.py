import sqlite3
from pathlib import Path

# Define database path relative to this file
DB_PATH = Path(__file__).parent / 'image_analysis.db'

def create_tables():
    """Create the necessary database tables if they don't exist"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Store information about images
    c.execute('''
        CREATE TABLE IF NOT EXISTS images (
            image_id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_path TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Store information about AI models/agents
    c.execute('''
        CREATE TABLE IF NOT EXISTS models (
            model_id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_name TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Store analysis results
    c.execute('''
        CREATE TABLE IF NOT EXISTS analysis_results (
            result_id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_id INTEGER,
            model_id INTEGER,
            description TEXT NOT NULL,
            humor_rating INTEGER CHECK (humor_rating >= 1 AND humor_rating <= 10),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (image_id) REFERENCES images (image_id),
            FOREIGN KEY (model_id) REFERENCES models (model_id),
            UNIQUE (image_id, model_id)
        )
    ''')
    
    conn.commit()
    conn.close()

def init_db():
    """Initialize database if it doesn't exist"""
    create_tables()

def save_analysis(image_path: str, model_name: str, result_dict: dict):
    """
    Save analysis results to database
    
    Args:
        image_path (str): Path to the analyzed image
        model_name (str): Name of the model used for analysis
        result_dict (dict): Dictionary containing 'image_description' and 'rating' keys
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        # Insert or get image
        c.execute('INSERT OR IGNORE INTO images (image_path) VALUES (?)', (image_path,))
        c.execute('SELECT image_id FROM images WHERE image_path = ?', (image_path,))
        image_id = c.fetchone()[0]
        
        # Insert or get model
        c.execute('INSERT OR IGNORE INTO models (model_name) VALUES (?)', (model_name,))
        c.execute('SELECT model_id FROM models WHERE model_name = ?', (model_name,))
        model_id = c.fetchone()[0]
        
        # Save analysis result
        c.execute('''
            INSERT INTO analysis_results 
            (image_id, model_id, description, humor_rating)
            VALUES (?, ?, ?, ?)
        ''', (image_id, model_id, result_dict['image_description'], result_dict['rating']))
        
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        conn.rollback()
    finally:
        conn.close()

def get_image_analyses(image_path: str):
    """
    Retrieve all analyses for a specific image
    
    Args:
        image_path (str): Path to the image
    Returns:
        list: List of dictionaries containing analysis results
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        c.execute('''
            SELECT m.model_name, ar.description, ar.humor_rating, ar.created_at
            FROM analysis_results ar
            JOIN images i ON ar.image_id = i.image_id
            JOIN models m ON ar.model_id = m.model_id
            WHERE i.image_path = ?
            ORDER BY ar.created_at DESC
        ''', (image_path,))
        
        results = [{
            'model': row[0],
            'description': row[1],
            'rating': row[2],
            'timestamp': row[3]
        } for row in c.fetchall()]
        
        return results
    finally:
        conn.close()

def get_model_analyses(model_name: str, limit: int = 10):
    """
    Retrieve recent analyses from a specific model
    
    Args:
        model_name (str): Name of the model
        limit (int): Maximum number of results to return
    Returns:
        list: List of dictionaries containing analysis results
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        c.execute('''
            SELECT i.image_path, ar.description, ar.humor_rating, ar.created_at
            FROM analysis_results ar
            JOIN images i ON ar.image_id = i.image_id
            JOIN models m ON ar.model_id = m.model_id
            WHERE m.model_name = ?
            ORDER BY ar.created_at DESC
            LIMIT ?
        ''', (model_name, limit))
        
        return [{
            'image_path': row[0],
            'description': row[1],
            'rating': row[2],
            'timestamp': row[3]
        } for row in c.fetchall()]
    finally:
        conn.close()