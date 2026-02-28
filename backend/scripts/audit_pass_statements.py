import os
import ast
from pathlib import Path

def analyze_pass_statements(search_dir):
    search_path = Path(search_dir)
    total_files = 0
    python_files = 0
    pass_occurrences = []

    for root, _, files in os.walk(search_path):
        for file in files:
            total_files += 1
            if not file.endswith(".py"):
                continue
            
            python_files += 1
            file_path = Path(root) / file
            try:
                content = file_path.read_text(encoding="utf-8")
                tree = ast.parse(content, filename=str(file_path))
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Pass):
                        pass_occurrences.append({
                            "file": str(file_path.relative_to(search_path)),
                            "line": node.lineno
                        })
            except Exception as e:
                # Ignore files that fail to parse
                pass

    print(f"Löydetyt `pass` -lausekkeet: {len(pass_occurrences)}")
    print(f"Käydyt Python-ohjelmat ({python_files}) ja Kaikki tiedostot ({total_files})")
    
    # Sort files by name for consistent output
    pass_occurrences.sort(key=lambda x: (x["file"], x["line"]))
    for occ in pass_occurrences:
        print(f"{occ['file']} (Rivi {occ['line']})")

if __name__ == "__main__":
    # Point the directory to the parent backend folder to match previous behavior
    base_dir = Path(__file__).resolve().parent.parent
    analyze_pass_statements(str(base_dir))
