import sys
from pathlib import Path

# Add parent directory to path so we can import backend modules
# This handles both running as script (python backend/init_db.py) 
# and as module (python -m backend.init_db)
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from backend.db import engine
from backend.models import Base


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully :3")
