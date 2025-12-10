import sys
import os
import importlib

# Add current directory to sys.path
sys.path.append(os.getcwd())

print(f"CWD: {os.getcwd()}")
print(f"sys.path: {sys.path}")

try:
    module = importlib.import_module("backend.agents.guard")
    print(f"Successfully imported {module}")
except ImportError as e:
    print(f"Failed to import: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
