import os
import re

TEST_DIR = 'backend_v2/tests/unit'

def fix_annotations(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Match single-line function definitions without a return type
    # Covers: def func_name(...) :
    # Covers: async def func_name(...) :
    pattern = re.compile(r'^(\s*(?:async\s+)?def\s+[a-zA-Z0-9_]+\s*\([^)]*\))\s*:', re.MULTILINE)
    
    def replacer(match):
        return match.group(1) + ' -> None:'

    new_content = pattern.sub(replacer, content)

    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed annotations in {filepath}")

for root, _, files in os.walk(TEST_DIR):
    for file in files:
        if file.endswith('.py'):
            fix_annotations(os.path.join(root, file))

# Fix main.py unused type: ignore and missing return type
try:
    with open('backend_v2/main.py', 'r', encoding='utf-8') as f:
        main_content = f.read()
    
    # Simple fix for main.py missing return types on lifespan
    main_content = re.sub(r'(async def lifespan\([^)]*\))\s*:', r'\1 -> None:', main_content)
    main_content = main_content.replace('  # type: ignore', '')
    
    with open('backend_v2/main.py', 'w', encoding='utf-8') as f:
        f.write(main_content)
    print("Fixed annotations in backend_v2/main.py")
except Exception as e:
    print(f"Error fixing main.py: {e}")

print("Done! Run the audit loop again.")
