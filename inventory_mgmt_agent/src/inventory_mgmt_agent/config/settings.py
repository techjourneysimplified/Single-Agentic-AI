import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Database settings
DB_PATH = BASE_DIR / "data" / "inventory1.db"

print(f"DB_PATH: {DB_PATH}") 

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

LOG_DIR = BASE_DIR / "logs"
os.makedirs(LOG_DIR, exist_ok=True)