import sqlite3
from pathlib import Path

# Define database path relative to this file
DB_PATH = Path(__file__).parent / 'image_analysis.db'

def create_tables():
    """Create the necessary database tables if they don't exist"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    #create consensus info. which has a limited lifespan.
    c.execute('''
        CREATE TABLE IF NOT EXISTS consensus (
            consensus_id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            current_step INTEGER NOT NULL DEFAULT 0,
            is_complete BOOLEAN NOT NULL DEFAULT FALSE,
            UNIQUE(consensus_id)
        )
    ''')


    # Store information about images
    c.execute('''
        CREATE TABLE IF NOT EXISTS images (
            image_id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_path TEXT UNIQUE NOT NULL,
            consensus_id INTEGER,
            FOREIGN KEY (consensus_id) REFERENCES consensus (consensus_id)
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
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id INTEGER NOT NULL,
            image_id INTEGER NOT NULL,
            consensus_id INTEGER NOT NULL,
            step INTEGER NOT NULL,
            choice INTEGER NOT NULL CHECK (choice IN (0, 1)),
            description TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (agent_id) REFERENCES models (model_id),
            FOREIGN KEY (image_id) REFERENCES images (image_id),
            FOREIGN KEY (consensus_id) REFERENCES consensus (consensus_id),
            UNIQUE (agent_id, image_id, consensus_id)
        )
    ''')
    
    
    conn.commit()
    conn.close()

def init_db():
    """Initialize database if it doesn't exist"""
    create_tables()


def create_consensus() -> int:
    """Create a new consensus round and return its ID"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO consensus (created_at, current_step, is_complete)
            VALUES (CURRENT_TIMESTAMP, 0, FALSE)
        ''')
        consensus_id = c.lastrowid
        conn.commit()
        return consensus_id
    finally:
        conn.close()

def cast_vote(image_path: str, model_name: str, consensus_id: int, step: int, 
              choice: float, description: str) -> None:
    """Cast a vote from a local model"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        # Get or create image record
        c.execute('INSERT OR IGNORE INTO images (image_path) VALUES (?)', (image_path,))
        c.execute('SELECT image_id FROM images WHERE image_path = ?', (image_path,))
        image_id = c.fetchone()[0]
        
        # Get or create model record
        c.execute('INSERT OR IGNORE INTO models (model_name) VALUES (?)', (model_name,))
        c.execute('SELECT model_id FROM models WHERE model_name = ?', (model_name,))
        model_id = c.fetchone()[0]
        
        # Insert vote
        c.execute('''
            INSERT INTO votes (agent_id, image_id, consensus_id, step, choice, description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (model_id, image_id, consensus_id, step, choice, description))
        
        conn.commit()
    finally:
        conn.close()

def record_external_vote(external_model_name: str, image_path: str, consensus_id: int,
                        step: int, choice: float, description: str) -> None:
    """Record a vote received from an external model"""
    # This is essentially the same as cast_vote, but might include additional 
    # validation or logging for external sources
    cast_vote(image_path, external_model_name, consensus_id, step, choice, description)