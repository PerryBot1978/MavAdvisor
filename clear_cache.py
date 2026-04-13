#!/usr/bin/env python3
"""
Clear Python cache (__pycache__ and .pyc files) from the project.
Run from the project root directory.
"""

import os
import shutil
from pathlib import Path

def clear_pycache(directory="."):
    """Recursively remove all __pycache__ directories and .pyc files."""
    removed_count = 0
    
    for root, dirs, files in os.walk(directory):
        # Remove __pycache__ directories
        if "__pycache__" in dirs:
            cache_path = os.path.join(root, "__pycache__")
            try:
                shutil.rmtree(cache_path)
                print(f"Removed: {cache_path}")
                removed_count += 1
            except Exception as e:
                print(f"Error removing {cache_path}: {e}")
        
        # Remove .pyc files
        for file in files:
            if file.endswith(".pyc"):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f"Removed: {file_path}")
                    removed_count += 1
                except Exception as e:
                    print(f"Error removing {file_path}: {e}")
    
    print(f"\n✓ Cache cleared. Removed {removed_count} cache items.")

if __name__ == "__main__":
    print("Clearing Python cache...")
    clear_pycache()
