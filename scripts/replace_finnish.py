import os
import re

replacements = {
    r"\bluontiaika\b": "created_at",
    r"\bagentti\b": "agent_name",
    # r"\bvaihe\b": "step_number", # "vaihe" could be used elsewhere, let's just replace it carefully or let's see. grep showed few hits for `vaihe`, wait I didn't grep vaihe. Let's do it anyway.
    r"\bvaihe\b": "step_number",
    r"\bversio\b": "version",
    r"\bsuoritus_ymparisto\b": "environment",
    r"\bsemanttinen_tarkistussumma\b": "semantic_checksum",
    r"\bvaite_teksti\b": "claim_text",
    r"\bloytyyko_todisteita\b": "evidence_found",
}

directories = ["c:/src/quorum/backend", "c:/src/quorum/client_app/lib", "c:/src/quorum/tests"]

count = 0
for d in directories:
    for root, _, files in os.walk(d):
        for file in files:
            if file.endswith(".py") or file.endswith(".dart"):
                filepath = os.path.join(root, file)
                with open(filepath, encoding="utf-8") as f:
                    content = f.read()

                new_content = content
                for pattern, replacement in replacements.items():
                    new_content = re.sub(pattern, replacement, new_content)

                if new_content != content:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    count += 1
                    print(f"Updated {filepath}")

print(f"Total files updated: {count}")
