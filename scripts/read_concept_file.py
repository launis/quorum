
file_path = r'c:\Users\risto\OneDrive\quorum\data\Holistinen Mestaruus.txt'
try:
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        print(f.read())
except Exception as e:
    print(f"Error reading file: {e}")
