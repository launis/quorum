import os
import re

domain_dir = r'C:\src\quorum\backend_v2\models\domain'

for filename in os.listdir(domain_dir):
    if not filename.endswith('.py'): continue
    filepath = os.path.join(domain_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Make fields optional
    content = re.sub(r'(history_text):\s*str\s*=\s*Field\(\.\.\.,', r'\1: str | None = Field(None,', content)
    content = re.sub(r'(product_text):\s*str\s*=\s*Field\(\.\.\.,', r'\1: str | None = Field(None,', content)
    content = re.sub(r'(reflection_text):\s*str\s*=\s*Field\(\.\.\.,', r'\1: str | None = Field(None,', content)
    
    # Fix validate_non_empty and similar validators to handle None
    # We'll just replace 'def validate_non_empty(cls, v: str) -> str:' with 'def validate_non_empty(cls, v: str | None) -> str | None:'
    # and add 'if v is None: return v'
    
    def replacer(match):
        header = match.group(0)
        # return the updated header
        return header.replace('v: str', 'v: str | None').replace('-> str:', '-> str | None:') + '\n        if v is None:\n            return v'

    # Catch standard validator pattern
    content = re.sub(r'def \w+\(cls,\s+v:\s+str\)\s*->\s*str:', replacer, content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print('Done refactoring domain models.')
