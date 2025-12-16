import os
import ast
import sys

# Threads to flag
FILE_LINE_LIMIT = 400
FUNC_LINE_LIMIT = 60

def analyze_file(filepath):
    issues = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            line_count = len(lines)
            content = "".join(lines)
            
        if line_count > FILE_LINE_LIMIT:
            issues.append(f"[FILE TOO LONG] {line_count} lines (Limit: {FILE_LINE_LIMIT})")
            
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Calculate function length
                    # end_lineno might be None in older python versions or partial trees, 
                    # but usually present in 3.8+
                    if hasattr(node, 'end_lineno') and hasattr(node, 'lineno'):
                        length = node.end_lineno - node.lineno
                        if length > FUNC_LINE_LIMIT:
                            issues.append(f"[FUNC TOO LONG] '{node.name}' is {length} lines (Limit: {FUNC_LINE_LIMIT})")
        except SyntaxError:
            pass # Skip syntax errors, handled by other audits
            
    except Exception as e:
        return [f"ANALYSIS FAILED: {str(e)}"]

    return issues

def main():
    backend_dir = os.path.join(os.getcwd(), 'backend')
    print(f"Analyzing Code Complexity in: {backend_dir}")
    print(f"Criteria: File > {FILE_LINE_LIMIT} lines, Function > {FUNC_LINE_LIMIT} lines.\n")
    
    files_with_issues = 0
    
    for root, dirs, files in os.walk(backend_dir):
        if "__pycache__" in root:
            continue
            
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, os.getcwd())
                
                issues = analyze_file(filepath)
                if issues:
                    files_with_issues += 1
                    print(f"\n{rel_path}:")
                    for issue in issues:
                        print(f"  - {issue}")

if __name__ == "__main__":
    main()
