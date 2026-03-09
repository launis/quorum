import os
import re

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # Nomenclature Refactoring for Component
    content = re.sub(r'\bComponent\b', 'LegacyPromptBlock', content)
    content = re.sub(r'\bcomponent\b', 'legacy_prompt_block', content)

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
                    
    print(f"Total Component files modified: {modified_count}")

if __name__ == '__main__':
    main()
