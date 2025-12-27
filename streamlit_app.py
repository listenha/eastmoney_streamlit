"""Streamlit app entry point for Cloud deployment."""

import sys
from pathlib import Path

# Add src to path to allow imports
project_root = Path(__file__).parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Import the main app (this will execute the streamlit code)
from eastmoney_tool.ui.app import *

