"""Streamlit app entry point for Cloud deployment."""

import sys
from pathlib import Path

# Add src to path to allow imports
project_root = Path(__file__).parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Read and execute the app file directly
app_file_path = project_root / "src" / "eastmoney_tool" / "ui" / "app.py"
with open(app_file_path, 'r', encoding='utf-8') as f:
    code = f.read()

# Execute the code in the current namespace
exec(compile(code, str(app_file_path), 'exec'))