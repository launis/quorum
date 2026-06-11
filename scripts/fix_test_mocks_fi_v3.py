import os
import re

def fix_mocks(path):
    # Match any dictionary containing 'en' inside 'translations' dict or kwargs
    # Just look for {"en": <ANYTHING>} or 'en': <ANYTHING> and add 'fi': <ANYTHING> if it's missing.
    # This is slightly risky but since it's just test files, it's fine.
    
    pattern_dict = re.compile(r'([\'"]en[\'"]\s*:\s*([^,}]+))')
    
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
        
        # We need a smarter way: only replace 'en' if we see it in a context like "translations" or I18nText
        # Let's find `translations={...}` or `"translations": {...}`
        def process_translations(match):
            inner_block = match.group(2)
            if '"fi"' not in inner_block and "'fi'" not in inner_block:
                # Find the 'en' key and duplicate it for 'fi'
                en_match = re.search(r'([\'"]en[\'"]\s*:\s*([^}]+?))(?=\s*\}|,\s*[\'"])', inner_block)
                if en_match:
                    full_en = en_match.group(1)
                    val = en_match.group(2).strip()
                    # Append fi
                    new_inner = inner_block.replace(full_en, f'{full_en}, "fi": {val}')
                    return match.group(1) + new_inner + match.group(3)
            return match.group(0)
            
        # Match `"translations": { ... }` or `translations={ ... }`
        p = re.compile(r'(translations["\']?\s*[:=]\s*\{)(.*?)(})', flags=re.DOTALL)
        content = p.sub(process_translations, content)
        
        if content != original_content:
            with open(file, 'w', encoding='utf-8') as f:
                f.write(content)
                print(f"Fixed {file}")

if __name__ == "__main__":
    fix_mocks('c:/src/quorum/backend_v2/tests')
    fix_mocks('c:/src/quorum/backend_v2/llm/mock_data.py')
