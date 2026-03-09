import os
import re

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # Nomenclature Refactoring
    content = re.sub(r'\bUniversalMatrix\b', 'PromptBlock', content)
    content = re.sub(r'\buniversalMatrix\b', 'promptBlock', content)
    content = re.sub(r'\bMatrixDataType\b', 'BlockDataType', content)
    content = re.sub(r'\bDimension\b', 'Observation', content)
    content = re.sub(r'\bdimension\b', 'observation', content)
    
    # URL Paths
    content = content.replace('/api/v2/matrices', '/api/v2/prompt-blocks')
    content = content.replace('/api/v2/dimensions', '/api/v2/observations')
    content = content.replace('/api/v2/agents', '/api/v2/roles')

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    modified_count = 0
    for root, dirs, files in os.walk('client_app_v2/lib'):
        for file in files:
            if file.endswith('.dart'):
                filepath = os.path.join(root, file)
                if process_file(filepath):
                    print(f"Modified: {filepath}")
                    modified_count += 1
                    
    print(f"Total dart files modified: {modified_count}")

if __name__ == '__main__':
    main()
