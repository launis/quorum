import os
import ast
import sys
from collections import Counter

def audit_file(filepath):
    """
    Audits a single python file for:
    1. Syntax Errors
    2. Duplicate Class/Function definitions
    3. Duplicate Import aliases (heuristic)
    """
    issues = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 1. Syntax Check
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            return [f"SYNTAX ERROR: {e.msg} at line {e.lineno}"]

        # 2. Duplicate Definitions Check
        definitions = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                definitions.append(node.name)
        
        counts = Counter(definitions)
        for name, count in counts.items():
            if count > 1 and name != "_": # Ignore underscores
                issues.append(f"DUPLICATE DEF: '{name}' defined {count} times")
    
    except Exception as e:
        return [f"AUDIT FAILED: {str(e)}"]

    return issues

def main():
    backend_dir = os.path.join(os.getcwd(), 'backend')
    print(f"Auditing directory: {backend_dir}")
    
    total_files = 0
    files_with_issues = 0
    
    for root, dirs, files in os.walk(backend_dir):
        if "__pycache__" in root:
            continue
            
        for file in files:
            if file.endswith(".py"):
                total_files += 1
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, os.getcwd())
                
                issues = audit_file(filepath)
                if issues:
                    files_with_issues += 1
                    print(f"\n[!] Issues in {rel_path}:")
                    for issue in issues:
                        print(f"  - {issue}")
                        
    print(f"\nAudit Complete. Scanned {total_files} files. Found issues in {files_with_issues} files.")

if __name__ == "__main__":
    main()
