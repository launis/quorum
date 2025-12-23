
import os
import re

file_path = "frontend/components.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# We want to replace the whole block starting from 'if "_debug_dump" in result:' up to the return statement.
# The content is slightly different than previous because we manually patched it and formatting might vary.

# Regex to match the block loosely but reliably:
pattern = r'(if "_debug_dump" in result:.*?)(\s+return)'

replacement = r'''        # Debug Dump Access (Raw Data)
        if "Raw_Steps" in result:
             with st.expander("🛠️ Raw Data (Debug)"):
                 st.json(result["Raw_Steps"])
                 
                 import json
                 st.download_button(
                     label="📥 Lataa koko JSON",
                     data=json.dumps(result, indent=2, ensure_ascii=False),
                     file_name="full_report.json",
                     mime="application/json"
                 )
                 
        return'''

new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

if new_content == content:
    print("Could not find pattern to replace!")
else:
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Successfully updated frontend/components.py")
