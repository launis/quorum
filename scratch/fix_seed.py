import json
import re

seed_path = r"c:\src\quorum\backend_v2\seed\seed_data.json"

with open(seed_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace the specific pattern
# ". If (something). Otherwise." -> ", extract the quote. Otherwise, return null."
pattern = r"\. If ([^\.]+)\. Otherwise\."
replacement = r". If \1, extract the quote. Otherwise, return null."

new_content = re.sub(pattern, replacement, content)

with open(seed_path, "w", encoding="utf-8") as f:
    f.write(new_content)

print(f"Fixed seed data. Replacements made: {content.count('. Otherwise.')}")
