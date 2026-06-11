import os
import re

def fix_mocks(path):
    # Match JSON-style dict
    pattern1 = re.compile(r'({"default_locale":\s*["\']en["\'],\s*"translations":\s*{["\']en["\']:\s*("[^"]*"|\'[^\']*\'))(})')
    # Match kwargs-style dict
    pattern2 = re.compile(r'(translations\s*=\s*{\s*["\']en["\']:\s*("[^"]*"|\'[^\']*\'))(})')
    
    if os.path.isfile(path):
        files = [path]
    else:
        files = []
        for root, _, fs in os.walk(path):
            for f in fs:
                if f.endswith('.py'):
                    files.append(os.path.join(root, f))
                    
    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        original_content = content
        
        content = pattern1.sub(r'\1, "fi": \2\3', content)
        content = pattern2.sub(r'\1, "fi": \2\3', content)
        
        if content != original_content:
            with open(file, 'w', encoding='utf-8') as f:
                f.write(content)
                print(f"Fixed {file}")

if __name__ == "__main__":
    fix_mocks('c:/src/quorum/backend_v2/tests')
    fix_mocks('c:/src/quorum/backend_v2/llm/mock_data.py')
