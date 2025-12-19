import os
import shutil

try:
    if os.path.exists("error.log"):
        shutil.copy("error.log", "error_log_safe.txt")
        print("Copied successfully.")
    else:
        print("error.log not found.")
except Exception as e:
    print(f"Error: {e}")
