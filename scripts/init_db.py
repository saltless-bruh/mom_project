import os
import sys
import sqlite3
import shutil
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).parent.parent.absolute()
sys.path.append(str(ROOT_DIR))

DB_PATH = ROOT_DIR / "data" / "maas.db"
SCHEMA_PATH = ROOT_DIR / "app" / "models" / "schema.sql"

def init_db():
    print(f"Initializing database at {DB_PATH}...")
    
    # Ensure data directory exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Check if DB exists to avoid accidental overwrite (optional, or just migrate)
    # For MVP, we will apply schema via 'IF NOT EXISTS'
    
    try:
        conn = sqlite3.connect(DB_PATH)
        
        # Enable WAL mode for concurrency
        conn.execute("PRAGMA journal_mode=WAL;")
        print("WAL mode enabled.")
        
        # Read and apply schema
        with open(SCHEMA_PATH, 'r') as f:
            schema_script = f.read()
            conn.executescript(schema_script)
            
        conn.commit()
        conn.close()
        print("Database schema applied successfully.")
        
        # Optional: Set file permissions (Windows specific handling might be needed, but chmod works for basic attrs)
        try:
            os.chmod(DB_PATH, 0o600) # Read/Write for owner only
            print("File permissions set (0o600).")
        except Exception as e:
            print(f"Warning: Could not set file permissions: {e}")

    except Exception as e:
        print(f"ERROR: Failed to initialize database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_db()
