import os

def check_db_file():
    path = 'c:/src/quorum/data/db.json'
    print(f"Checking {path}")
    if os.path.exists(path):
        size = os.path.getsize(path)
        print(f"Size: {size} bytes")
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read(1000)
            print(f"Head: {content}")
    else:
        print("File not found.")

if __name__ == "__main__":
    check_db_file()
