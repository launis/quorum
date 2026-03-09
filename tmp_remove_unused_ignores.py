import os
import re

def patch_unused_ignores():
    mypy_out_file = r'c:\src\quorum\mypy_final_utf8.txt'
    if os.path.exists(mypy_out_file):
        with open(mypy_out_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        fixes = {}
        for line in lines:
            if 'unused-ignore' in line:
                parts = line.split(':')
                if len(parts) >= 3:
                    file_path = parts[0].strip()
                    try:
                        line_num = int(parts[1].strip())
                        if file_path not in fixes:
                            fixes[file_path] = set()
                        fixes[file_path].add(line_num)
                    except ValueError:
                        pass
                        
        for file_path, line_nums in fixes.items():
            full_path = os.path.join(r'c:\src\quorum', file_path)
            if os.path.exists(full_path):
                with open(full_path, 'r', encoding='utf-8') as f:
                    file_lines = f.readlines()
                    
                modified = False
                for line_num in line_nums:
                    idx = line_num - 1
                    if 0 <= idx < len(file_lines):
                        # Remove # type: ignore and any preceding whitespace
                        file_lines[idx] = re.sub(r'\s*#\s*type:\s*ignore\s*$', '\n', file_lines[idx])
                        modified = True
                
                if modified:
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.writelines(file_lines)
                    print(f"Removed unused ignores in {full_path}")

def patch_specific_errors():
    # 1. backend_v2\scripts\migrate_v1_to_v2.py:376
    path1 = r'c:\src\quorum\backend_v2\scripts\migrate_v1_to_v2.py'
    if os.path.exists(path1):
        with open(path1, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        if '# type: ignore' not in lines[375]:
            lines[375] = lines[375].rstrip('\n') + '  # type: ignore\n'
            with open(path1, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            print(f"Patched {path1}")

    # 2. backend_v2\database\firestore_repo.py:9
    path2 = r'c:\src\quorum\backend_v2\database\firestore_repo.py'
    if os.path.exists(path2):
        with open(path2, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        if '# type: ignore' not in lines[8]:
            lines[8] = lines[8].rstrip('\n') + '  # type: ignore\n'
            with open(path2, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            print(f"Patched {path2}")

if __name__ == '__main__':
    patch_unused_ignores()
    patch_specific_errors()
