
try:
    with open(r"c:\src\quorum\analysis_large_content.txt", "r", encoding="utf-8") as f:
            if line.startswith("FOUND at"):
                parts = line.split("->")
                if len(parts) > 1:
                    comp_id = parts[1].strip()
                    length = line.split("Length=")[1].strip() if "Length=" in line else "?"
                    print(f"Component: {comp_id} | Size: {length}")
except Exception as e:
    print(f"Error: {e}")
