
import os
import glob
import time

TARGET_DIR = "tests/output"

def force_cleanup():
    if not os.path.exists(TARGET_DIR):
        print(f"{TARGET_DIR} does not exist.")
        return

    files = glob.glob(os.path.join(TARGET_DIR, "*.txt"))
    for f in files:
        if "safe_log.txt" in f:
            continue # Don't delete our own log file while writing to it in other process
        
        try:
            os.remove(f)
            print(f"Deleted {f}")
        except Exception as e:
            print(f"Failed to delete {f}: {e}")

if __name__ == "__main__":
    force_cleanup()
