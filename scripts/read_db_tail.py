
import os

file_path = r'c:\Users\risto\OneDrive\quorum\data\db.json'
file_size = os.path.getsize(file_path)
read_size = 50000  # Read last 50KB to be safe

with open(file_path, 'rb') as f:
    if file_size > read_size:
        f.seek(file_size - read_size)
    content = f.read().decode('utf-8', errors='ignore')
    print(content)
