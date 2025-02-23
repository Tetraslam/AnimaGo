import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import uvicorn

# Now we can import our modules
from src.server.app import app

if __name__ == "__main__":
    uvicorn.run(
        "src.server.app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_excludes=[".venv/"],
        env_file="../.env"
    ) 