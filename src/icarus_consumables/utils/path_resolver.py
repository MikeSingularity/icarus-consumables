import os
import sys
from pathlib import Path

def get_project_root() -> Path:
    """Returns the project root directory."""
    # If running from src/utils/
    script_path = Path(__file__).resolve()
    # Assuming src/utils/path_resolver.py
    if "src" in script_path.parts:
        # The project root is the parent of the 'src' directory
        return script_path.parents[len(script_path.parts) - script_path.parts.index("src") - 1]
    return script_path.parent

def resolve_path(relative_path: str) -> Path:
    """Resolves a path relative to the project root."""
    return get_project_root() / relative_path
