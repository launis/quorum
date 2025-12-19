

file_path = r'c:\Users\risto\OneDrive\quorum\data\Holistinen Mestaruus.txt'
output_path = r'c:\Users\risto\OneDrive\quorum\data\bib_output.txt'
try:
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        f.seek(0, 2)
        size = f.tell()
        start = max(0, size - 10000)
        f.seek(start)
        data = f.read()
        
    with open(output_path, 'w', encoding='utf-8') as out:
        out.write(data)
    print(f"Dumped tail to {output_path}")

except Exception as e:
    print(f"Error: {e}")

