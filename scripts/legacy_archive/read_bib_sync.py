
# Sync read of tail
file_path = r'c:\Users\risto\OneDrive\quorum\data\Holistinen Mestaruus.txt'
try:
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        f.seek(0, 2)
        size = f.tell()
        start = max(0, size - 15000) # 15KB should cover bibliography
        f.seek(start)
        lines = f.readlines()
        
    start_printing = False
    count = 0
    for line in lines:
        if "Lähdeluettelo" in line or "Lähteet" in line:
            start_printing = True
        
        # Fallback: if we are near the end (last 100 lines) and haven't found header, just print
        if len(lines) - count < 200: 
             start_printing = True
             
        if start_printing:
            print(line.strip())
        count += 1
        
except Exception as e:
    print(f"Error: {e}")
