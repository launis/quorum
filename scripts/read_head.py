
try:
    with open(r"c:\src\quorum\db_snapshot.txt", "r", encoding="utf-8") as f:
        for i in range(50):
            line = f.readline()
            if not line: break
            print(line.strip())
except Exception as e:
    print(f"Error: {e}")
