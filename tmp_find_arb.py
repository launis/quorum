import json
import os
import re

arb_path = r"c:\src\quorum\client_app_v2\lib\l10n\app_en.arb"
lib_path = r"c:\src\quorum\client_app_v2\lib"

with open(arb_path, "r", encoding="utf-8") as f:
    arb_data = json.load(f)

# Extract keys (ignore metadata starting with @)
keys = [k for k in arb_data.keys() if not k.startswith("@@") and not k.startswith("@")]

# Read all dart files
dart_files_content = []
for root, _, files in os.walk(lib_path):
    for file in files:
        if file.endswith(".dart"):
            with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                dart_files_content.append(f.read())

all_content = "\n".join(dart_files_content)

unused_keys = []
for key in keys:
    # Look for exact word matches of the key, usually prefixed by a dot like .myKey or inside string if dynamic
    # But usually it's AppLocalizations.of(context)!.myKey
    # So searching the exact string `key` with word boundaries is safe
    pattern = r"\b" + re.escape(key) + r"\b"
    if not re.search(pattern, all_content):
        unused_keys.append(key)

print(f"Total keys: {len(keys)}")
print(f"Unused keys: {len(unused_keys)}")
for uk in unused_keys:
    print(f" - {uk}")

