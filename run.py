"""Launch script for CodeRover agent."""

import sys
import os

# Ensure project root is in path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import and run main
from src.main import main

if __name__ == "__main__":
    main()