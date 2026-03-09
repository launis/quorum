import os
import re

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # 1. Fix V1 to V2 imports. Only match "backend." at word boundary
    # to avoid messing up things that might happen to contain backend.
    content = re.sub(r'from backend\.', 'from backend_v2.', content)
    content = re.sub(r'import backend\.', 'import backend_v2.', content)

    # 2. Nomenclature Refactoring (with word boundaries to be safe)
    content = re.sub(r'\bUniversalMatrix\b', 'PromptBlock', content)
    content = re.sub(r'\bMatrixDataType\b', 'BlockDataType', content)
    content = re.sub(r'\bDimension\b', 'Observation', content)
    content = re.sub(r'\bAgent\b', 'Role', content)
    
    # Also fix some specific references to avoid breaking
    # e.g., if we changed Agent to Role, what if there's a Role model for Users?
    # backend.models.auth handles UserRole. So "Role" as a standalone class is fine.
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    modified_count = 0
    for root, dirs, files in os.walk('backend_v2'):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                if process_file(filepath):
                    print(f"Modified: {filepath}")
                    modified_count += 1
                    
    print(f"Total files modified: {modified_count}")

if __name__ == '__main__':
    main()
