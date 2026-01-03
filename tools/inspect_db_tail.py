
import os

DB_PATH = "c:/Users/risto/OneDrive/quorum/data/db.json"

def inspect_tail():
    try:
        size = os.path.getsize(DB_PATH)
        print(f"File size: {size} bytes")
        
        with open(DB_PATH, 'rb') as f:
            # Read last 200 bytes
            f.seek(max(0, size - 200))
            tail = f.read()
            print(f"Tail (last 200 bytes): {tail}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_tail()
